"""
Роутер для работы с медиафайлами
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import magic

from database.session import get_db
from .. import schemas
from ..crud import (
    create_media, get_media_by_id, get_media_by_user, get_temp_media_by_user,
    update_media, confirm_temp_media, delete_media, delete_old_temp_media,
    get_user_temp_media_count, search_media, get_media_by_page
)
from ..dependencies import get_current_user_id, get_media_or_404, validate_user_access
from ..utils import (
    ensure_user_directories, generate_filename, get_file_extension,
    get_media_type, validate_file_size, validate_file_extension,
    save_uploaded_file, get_file_info, move_to_permanent,
    delete_file, get_file_url, cleanup_old_temp_files
)
from ..config import config

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload", response_model=schemas.MediaUploadResponse)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    page_id: Optional[uuid.UUID] = Form(None),
    is_public: bool = Form(False),
    is_temp: bool = Form(True),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Загрузка медиафайла.
    
    - **file**: Файл для загрузки
    - **page_id**: ID страницы (опционально, для постоянных медиа)
    - **is_public**: Публичный доступ (по умолчанию False)
    - **is_temp**: Временный файл (по умолчанию True)
    """
    # Проверяем размер файла
    file_content = await file.read()
    file_size = len(file_content)
    
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Размер файла превышает максимальный ({config.MAX_FILE_SIZE / (1024*1024)} MB)"
        )
    
    # Определяем MIME-тип и расширение
    mime_type = magic.from_buffer(file_content, mime=True)
    file_extension = get_file_extension(file.filename)
    media_type = get_media_type(mime_type, file_extension)
    
    # Проверяем расширение файла
    if not validate_file_extension(file_extension, media_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Расширение файла .{file_extension} не поддерживается для типа {media_type}"
        )
    
    # Для временных файлов проверяем лимит
    if is_temp:
        temp_count = get_user_temp_media_count(db, user_id)
        if temp_count >= 50:  # Максимум 50 временных файлов на пользователя
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Превышен лимит временных файлов. Удалите старые или подтвердите их."
            )
    
    # Получаем информацию о файле (ширина, высота, длительность)
    width, height, duration = None, None, None
    if media_type in ['image', 'video']:
        # Сохраняем временно для анализа
        temp_id = str(uuid.uuid4())
        temp_filename = f"temp_{temp_id}.{file_extension}"
        temp_path = save_uploaded_file(file_content, temp_filename, user_id, page_id, is_temp=True)
        width, height, duration = get_file_info(temp_path)
        os.remove(temp_path)  # Удаляем временный файл
    
    # Создаем ID для медиа
    media_id = uuid.uuid4()
    filename = generate_filename(file.filename, media_id)
    
    # Сохраняем файл
    save_uploaded_file(file_content, filename, user_id, page_id, is_temp=is_temp)
    
    # Создаем запись в БД
    media_data = schemas.MediaCreate(
        user_id=user_id,
        page_id=page_id,
        file_extension=file_extension,
        file_size=file_size,
        media_type=media_type,
        mime_type=mime_type,
        width=width,
        height=height,
        duration=duration,
        is_public=is_public,
        is_temp=is_temp
    )
    
    db_media = create_media(db, media_data)
    
    # Генерируем URL
    url = get_file_url(filename, user_id, page_id, is_temp)
    temp_url = url if is_temp else None
    
    # Для временных файлов добавляем задачу очистки
    if is_temp:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=config.TEMP_FILE_LIFETIME)
        background_tasks.add_task(cleanup_old_temp_files, config.TEMP_FILE_LIFETIME)
    else:
        expires_at = None
    
    return schemas.MediaUploadResponse(
        id_media=db_media.id_media,
        filename=filename,
        url=url,
        temp_url=temp_url,
        expires_at=expires_at,
        message="Файл успешно загружен"
    )


@router.get("/{media_id}", response_model=schemas.MediaResponse)
def get_media(
    media = Depends(get_media_or_404),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Получение информации о медиа"""
    # Проверяем доступ
    if not media.is_public and media.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому медиа"
        )
    
    return media


@router.get("/", response_model=schemas.MediaListResponse)
def list_media(
    user_id: uuid.UUID = Depends(get_current_user_id),
    page_id: Optional[uuid.UUID] = None,
    media_type: Optional[str] = None,
    is_temp: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Получение списка медиа с фильтрами"""
    if page_size > config.MAX_PAGE_SIZE:
        page_size = config.MAX_PAGE_SIZE
    
    skip = (page - 1) * page_size
    
    # Поиск медиа
    media_list = search_media(
        db, user_id=user_id, page_id=page_id,
        media_type=media_type, is_temp=is_temp,
        skip=skip, limit=page_size
    )
    
    # Получаем общее количество
    total = len(search_media(
        db, user_id=user_id, page_id=page_id,
        media_type=media_type, is_temp=is_temp
    ))
    
    return schemas.MediaListResponse(
        media=media_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/temp/my", response_model=schemas.MediaListResponse)
def get_my_temp_media(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение временных медиа текущего пользователя"""
    temp_media = get_temp_media_by_user(db, user_id)
    
    return schemas.MediaListResponse(
        media=temp_media,
        total=len(temp_media),
        page=1,
        page_size=len(temp_media)
    )


@router.post("/{media_id}/confirm", response_model=schemas.MediaConfirmResponse)
def confirm_media(
    media_id: uuid.UUID,
    request: schemas.MediaConfirmRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Подтверждение временного медиа (привязка к странице)"""
    media = get_media_or_404(media_id, db)
    validate_user_access(media, user_id)
    
    if not media.is_temp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Медиа уже является постоянным"
        )
    
    # Обновляем медиа
    updated_media = confirm_temp_media(db, media_id, request.page_id)
    if not updated_media:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при подтверждении медиа"
        )
    
    # Перемещаем файл
    # Имя файла теперь включает дату, нужно получить его из записи в БД
    # Ищем файл в папке пользователя
    import glob
    user_temp_folder = config.get_temp_folder_path(user_id)
    pattern = os.path.join(user_temp_folder, f"{media_id}_*.*")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        # Если не нашли по шаблону, пробуем старое имя
        old_filename = f"{media_id}.{media.file_extension}"
        old_path = os.path.join(user_temp_folder, old_filename)
        if os.path.exists(old_path):
            filename = old_filename
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
    else:
        # Берем первый найденный файл
        filename = os.path.basename(matching_files[0])
    
    if not move_to_permanent(filename, filename, user_id, request.page_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при перемещении файла"
        )
    
    return schemas.MediaConfirmResponse(
        id_media=updated_media.id_media,
        is_temp=updated_media.is_temp,
        page_id=updated_media.page_id,
        message="Медиа успешно подтверждено"
    )


@router.put("/{media_id}", response_model=schemas.MediaResponse)
def update_media_info(
    media_id: uuid.UUID,
    media_update: schemas.MediaUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление информации о медиа"""
    media = get_media_or_404(media_id, db)
    validate_user_access(media, user_id)
    
    updated_media = update_media(db, media_id, media_update)
    if not updated_media:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении медиа"
        )
    
    return updated_media


@router.delete("/{media_id}")
def delete_media_file(
    media_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление медиа"""
    media = get_media_or_404(media_id, db)
    validate_user_access(media, user_id)
    
    # Ищем файл по шаблону (так как имя включает дату)
    import glob
    if media.is_temp:
        search_folder = config.get_temp_folder_path(user_id, media.page_id)
    else:
        search_folder = config.get_permanent_folder_path(user_id, media.page_id)
    
    pattern = os.path.join(search_folder, f"{media_id}_*.*")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        # Если не нашли по шаблону, пробуем старое имя
        old_filename = f"{media_id}.{media.file_extension}"
        old_path = os.path.join(search_folder, old_filename)
        if os.path.exists(old_path):
            filename = old_filename
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
    else:
        # Берем первый найденный файл
        filename = os.path.basename(matching_files[0])
    
    # Удаляем файл
    if not delete_file(filename, user_id, media.page_id, media.is_temp):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении файла"
        )
    
    # Удаляем запись из БД
    if not delete_media(db, media_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении записи"
        )
    
    return {"message": "Медиа успешно удалено"}


@router.post("/cleanup/temp", response_model=schemas.TempMediaCleanupResponse)
def cleanup_temp_media(
    hours_old: int = 24,
    db: Session = Depends(get_db)
):
    """Очистка старых временных медиа"""
    # Удаляем из БД
    db_deleted = delete_old_temp_media(db, hours_old)
    
    # Удаляем файлы
    file_deleted = cleanup_old_temp_files(hours_old)
    
    return schemas.TempMediaCleanupResponse(
        deleted_count=max(db_deleted, file_deleted),
        message=f"Удалено {max(db_deleted, file_deleted)} временных медиа"
    )


@router.get("/page/{page_id}", response_model=schemas.MediaListResponse)
def get_page_media(
    page_id: uuid.UUID,
    include_temp: bool = False,
    db: Session = Depends(get_db)
):
    """Получение медиа страницы"""
    media_list = get_media_by_page(db, page_id, include_temp)
    
    return schemas.MediaListResponse(
        media=media_list,
        total=len(media_list),
        page=1,
        page_size=len(media_list)
    )