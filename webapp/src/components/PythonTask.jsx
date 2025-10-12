import { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import WebApp from '@twa-dev/sdk'
import { API_BASE } from '../config'
import './PythonTask.css'

function PythonTask({ userId }) {
  const [task, setTask] = useState(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [showHint, setShowHint] = useState(false)

  useEffect(() => {
    fetchTask()
  }, [userId])

  const fetchTask = async () => {
    if (!userId) return

    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/code/task/?user_id=${userId}`)
      const data = await response.json()

      if (response.ok) {
        setTask(data)
        setCode(data.starter_code || '# Напишите ваш код здесь\nimport pandas as pd\nimport numpy as np\n\n')
        setResult(null)
        setShowHint(false)
      } else {
        WebApp.showAlert(data.error || 'Не удалось загрузить задачу')
      }
    } catch (error) {
      console.error('Error fetching task:', error)
      WebApp.showAlert('Ошибка при загрузке задачи')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!task || !userId) return

    setSubmitting(true)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/code/submit/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          question_id: task.id,
          code: code,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)

        if (data.passed) {
          WebApp.showAlert('🎉 Отлично! Все тесты пройдены!', () => {
            // Auto-load next task after success
            fetchTask()
          })
        }
      } else {
        WebApp.showAlert('Ошибка при отправке решения')
      }
    } catch (error) {
      console.error('Error submitting code:', error)
      WebApp.showAlert('Ошибка при отправке решения')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="python-task loading">
        <div className="loading-spinner">⏳ Загрузка задачи...</div>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="python-task">
        <div className="no-task">
          <p>❌ Нет доступных задач</p>
          <p>Попробуйте выбрать другую тему или уровень сложности</p>
        </div>
      </div>
    )
  }

  return (
    <div className="python-task">
      <div className="task-header">
        <h2>💻 {task.topic}</h2>
        <span className={`difficulty-badge ${task.difficulty}`}>
          {task.difficulty}
        </span>
      </div>

      <div className="task-description">
        <h3>📝 Задание</h3>
        <p>{task.question_text}</p>
      </div>

      {task.hint && (
        <div className="task-hint">
          <button
            className="hint-toggle"
            onClick={() => setShowHint(!showHint)}
          >
            💡 {showHint ? 'Скрыть подсказку' : 'Показать подсказку'}
          </button>
          {showHint && <p className="hint-content">{task.hint}</p>}
        </div>
      )}

      <div className="editor-section">
        <h3>✍️ Ваше решение</h3>
        <Editor
          height="350px"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value)}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
          }}
        />
      </div>

      <div className="task-actions">
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={submitting || !code.trim()}
        >
          {submitting ? '⏳ Проверка...' : '✅ Проверить решение'}
        </button>
        <button
          className="skip-button"
          onClick={fetchTask}
          disabled={submitting}
        >
          ⏭️ Следующая задача
        </button>
      </div>

      {result && (
        <div className={`result ${result.passed ? 'success' : 'error'}`}>
          <h3>{result.passed ? '✅ Успешно!' : '❌ Не пройдено'}</h3>

          <div className="test-results">
            <h4>Результаты тестов:</h4>
            {result.test_results.map((test, index) => (
              <div key={index} className={`test-case ${test.passed ? 'passed' : 'failed'}`}>
                <div className="test-header">
                  <span className="test-number">Тест {test.test_number}</span>
                  <span className="test-status">
                    {test.passed ? '✅' : '❌'}
                  </span>
                </div>
                {!test.passed && (
                  <div className="test-details">
                    {test.error ? (
                      <p className="error-message">❗ {test.error}</p>
                    ) : (
                      <>
                        <p><strong>Ожидалось:</strong> {test.expected}</p>
                        <p><strong>Получено:</strong> {test.actual}</p>
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {result.passed && result.explanation && (
            <div className="explanation">
              <h4>💡 Объяснение:</h4>
              <p>{result.explanation}</p>
            </div>
          )}

          {task.documentation_link && (
            <div className="documentation">
              <a
                href={task.documentation_link}
                target="_blank"
                rel="noopener noreferrer"
                className="doc-link"
              >
                📖 Документация Pandas
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default PythonTask
