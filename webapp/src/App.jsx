import { useState, useEffect } from 'react'
import WebApp from '@twa-dev/sdk'
import QuestionList from './components/QuestionList'
import Documentation from './components/Documentation'
import CodeChallenge from './components/CodeChallenge'
import PythonTask from './components/PythonTask'
import './App.css'

function App() {
  const [view, setView] = useState('menu') // menu, questions, docs, code, task
  const [user, setUser] = useState(null)
  const [currentTopic, setCurrentTopic] = useState(null)

  useEffect(() => {
    // Initialize Telegram Web App
    WebApp.ready()
    WebApp.expand()

    // Set theme colors
    WebApp.setHeaderColor('#2481cc')
    WebApp.setBackgroundColor('#ffffff')

    // Get user data from Telegram
    const tgUser = WebApp.initDataUnsafe?.user
    if (tgUser) {
      setUser({
        id: tgUser.id,
        first_name: tgUser.first_name,
        username: tgUser.username
      })
    }

    // Check if we should start with task view (from bot deep link)
    const params = new URLSearchParams(window.location.search)
    const initialView = params.get('view')
    if (initialView === 'task') {
      setView('task')
    }

    // Setup back button
    WebApp.BackButton.onClick(() => {
      if (view !== 'menu') {
        setView('menu')
      }
    })

    return () => {
      WebApp.BackButton.offClick()
    }
  }, [view])

  useEffect(() => {
    // Show/hide back button based on view
    if (view === 'menu') {
      WebApp.BackButton.hide()
    } else {
      WebApp.BackButton.show()
    }
  }, [view])

  return (
    <div className="app">
      <header className="app-header">
        <h1>🐼 Learn Pandas</h1>
        {user && <p className="user-info">Привет, {user.first_name}!</p>}
      </header>

      <main className="app-content">
        {view === 'menu' && (
          <div className="menu">
            <button
              className="menu-button"
              onClick={() => setView('docs')}
            >
              📚 Документация
            </button>
            <button
              className="menu-button"
              onClick={() => setView('questions')}
            >
              📝 Вопросы
            </button>
            <button
              className="menu-button"
              onClick={() => setView('task')}
            >
              🎯 Задачи с проверкой
            </button>
            <button
              className="menu-button"
              onClick={() => setView('code')}
            >
              💻 Свободная практика
            </button>
          </div>
        )}

        {view === 'docs' && (
          <Documentation
            userId={user?.id}
            onTopicSelect={(topic) => {
              setCurrentTopic(topic)
              setView('questions')
            }}
          />
        )}

        {view === 'questions' && (
          <QuestionList
            userId={user?.id}
            topic={currentTopic}
          />
        )}

        {view === 'task' && (
          <PythonTask userId={user?.id} />
        )}

        {view === 'code' && (
          <CodeChallenge userId={user?.id} />
        )}
      </main>
    </div>
  )
}

export default App
