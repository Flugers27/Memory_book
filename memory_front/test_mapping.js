const data = {
  "memory_page_list": [
    {
      "full_name": "Test User",
      "gender": "M",
      "birth_date": "1990-01-01",
      "death_date": null,
      "place_of_birth": "",
      "place_of_death": "",
      "avatar_url": null,
      "is_human": true,
      "id_agent": "4ffe8792-6cff-4788-b83e-3ac6eb248b4b",
      "page": {
        "epitaph": "Память о тесте",
        "biography": [
          {
            "title": "Биография тестового пользователя",
            "info": "Это тестовый пользователь, созданный для проверки.",
            "titles": [
              {
                "title": "Хобби",
                "info": "Любит тестировать.",
                "titles": []
              }
            ]
          }
        ],
        "is_public": true,
        "is_draft": false,
        "id_page": "9cabc6d1-e491-49fb-be63-6749169d502f",
        "agent_id": "4ffe8792-6cff-4788-b83e-3ac6eb248b4b",
        "created_at": "2025-12-25T15:25:49.092014+03:00",
        "updated_at": "2025-12-25T15:25:49.092014+03:00"
      }
    }
  ]
};

function mapResponseToPages(data) {
  const list = data.memory_page_list || data.pages || [];
  return list.map((item) => ({
    id: item.page?.id_page || item.id,
    title: item.full_name || 'Без названия',
    epitaph: item.page?.epitaph || item.epitaph || '',
    biography: item.page?.biography || item.biography || '',
    is_public: item.page?.is_public ?? item.is_public ?? true,
    is_draft: item.page?.is_draft ?? item.is_draft ?? false,
    created_at: item.page?.created_at || item.created_at || new Date().toISOString(),
    agent_id: item.id_agent || item.agent_id,
  }));
}

const mapped = mapResponseToPages(data);
console.log('Mapped pages:', JSON.stringify(mapped, null, 2));
console.log('Biography type:', typeof mapped[0].biography);
console.log('Biography value:', mapped[0].biography);