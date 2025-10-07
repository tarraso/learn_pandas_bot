import { useState, useEffect } from 'react'
import axios from 'axios'
import './QuestionList.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

function QuestionList({ userId, topic }) {
  const [question, setQuestion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [answered, setAnswered] = useState(false)
  const [selectedOption, setSelectedOption] = useState(null)

  const loadQuestion = async () => {
    setLoading(true)
    setAnswered(false)
    setSelectedOption(null)

    try {
      const response = await axios.get(`${API_BASE}/questions/next/`, {
        params: { user_id: userId, topic_id: topic?.id }
      })
      setQuestion(response.data)
    } catch (error) {
      console.error('Error loading question:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      loadQuestion()
    }
  }, [userId, topic])

  const handleAnswer = async (option) => {
    setSelectedOption(option)
    setAnswered(true)

    try {
      await axios.post(`${API_BASE}/questions/answer/`, {
        user_id: userId,
        question_id: question.id,
        answer: option
      })
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  if (loading) {
    return <div className="question-loading">⏳ Загрузка вопроса...</div>
  }

  if (!question) {
    return <div className="question-empty">😔 Вопросы закончились!</div>
  }

  return (
    <div className="question-list">
      <div className="question-header">
        <span className="topic-badge">{question.topic}</span>
        <span className="difficulty-badge">{question.difficulty}</span>
      </div>

      <div className="question-text">
        <p>{question.question_text}</p>
      </div>

      {question.code_example && (
        <pre className="code-example">
          <code>{question.code_example}</code>
        </pre>
      )}

      <div className="options">
        {question.options.map((option) => {
          const letter = option.letter || option[0];
          const text = option.text || option[1];
          return (
            <button
              key={letter}
              className={`option-button ${
                answered
                  ? letter === question.correct_option
                    ? 'correct'
                    : letter === selectedOption
                    ? 'incorrect'
                    : ''
                  : ''
              }`}
              onClick={() => !answered && handleAnswer(letter)}
              disabled={answered}
            >
              <span className="option-letter">{letter}</span>
              <span className="option-text">{text}</span>
            </button>
          );
        })}
      </div>

      {answered && (
        <div className="explanation">
          <h3>💡 Объяснение:</h3>
          <p>{question.explanation}</p>
          {question.documentation_link && (
            <a href={question.documentation_link} target="_blank" rel="noopener noreferrer">
              📖 Документация Pandas
            </a>
          )}
        </div>
      )}

      {answered && (
        <button className="next-button" onClick={loadQuestion}>
          Следующий вопрос →
        </button>
      )}
    </div>
  )
}

export default QuestionList
