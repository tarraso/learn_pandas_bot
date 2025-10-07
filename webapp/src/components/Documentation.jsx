import { useState, useEffect } from 'react'
import axios from 'axios'
import './Documentation.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

function Documentation({ userId, onTopicSelect }) {
  const [topics, setTopics] = useState([])
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTopics()
  }, [])

  const loadTopics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/topics/`)
      setTopics(response.data)
    } catch (error) {
      console.error('Error loading topics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTopicClick = (topic) => {
    setSelectedTopic(topic)
  }

  const handleStartQuestions = () => {
    if (selectedTopic && onTopicSelect) {
      onTopicSelect(selectedTopic)
    }
  }

  if (loading) {
    return <div className="docs-loading">⏳ Загрузка тем...</div>
  }

  return (
    <div className="documentation">
      {!selectedTopic ? (
        <div className="topics-list">
          <h2>📚 Выберите тему</h2>
          {topics.map((topic) => (
            <button
              key={topic.id}
              className="topic-card"
              onClick={() => handleTopicClick(topic)}
            >
              <h3>{topic.name}</h3>
              {topic.description && <p>{topic.description}</p>}
            </button>
          ))}
        </div>
      ) : (
        <div className="topic-detail">
          <h2>{selectedTopic.name}</h2>
          {selectedTopic.documentation ? (
            <div className="documentation-content">
              <p>{selectedTopic.documentation}</p>
            </div>
          ) : (
            <p className="no-docs">Документация скоро появится...</p>
          )}
          <div className="action-buttons">
            <button className="secondary-button" onClick={() => setSelectedTopic(null)}>
              ← Назад к темам
            </button>
            <button className="primary-button" onClick={handleStartQuestions}>
              Начать тестирование →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Documentation
