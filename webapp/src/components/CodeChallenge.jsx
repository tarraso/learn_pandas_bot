import { useState } from 'react'
import Editor from '@monaco-editor/react'
import { usePyodide } from '../hooks/usePyodide'
import './CodeChallenge.css'

function CodeChallenge({ userId }) {
  const [code, setCode] = useState('import pandas as pd\nimport numpy as np\n\n# Напишите ваш код здесь\ndf = pd.DataFrame({\n    "A": [1, 2, 3],\n    "B": [4, 5, 6]\n})\n\nprint(df)')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const { pyodide, loading: pyodideLoading, error: pyodideError, loadingPackages, runPython } = usePyodide()

  const handleRun = async () => {
    setLoading(true)
    setResult(null)

    try {
      const result = await runPython(code)
      setResult(result)
    } finally {
      setLoading(false)
    }
  }

  const getButtonText = () => {
    if (loading) return '⏳ Выполняется...'
    if (loadingPackages) return '📦 Загрузка pandas...'
    return '▶️ Запустить'
  }

  const isRunDisabled = loading || pyodideLoading || pyodideError

  return (
    <div className="code-challenge">
      <h2>💻 Практика кода</h2>

      {/* Pyodide loading status */}
      {pyodideLoading && (
        <div className="pyodide-status loading">
          ⏳ Загрузка Python окружения... (это может занять ~30 секунд при первом запуске)
        </div>
      )}

      {pyodideError && (
        <div className="pyodide-status error">
          ❌ {pyodideError}
        </div>
      )}

      {pyodide && !pyodideLoading && (
        <div className="pyodide-status ready">
          ✅ Python готов к работе (выполняется в браузере)
        </div>
      )}

      <div className="editor-container">
        <Editor
          height="300px"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value)}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>

      <button
        className="run-button"
        onClick={handleRun}
        disabled={isRunDisabled}
      >
        {getButtonText()}
      </button>

      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          <h3>{result.success ? '✅ Успешно' : '❌ Ошибка'}</h3>
          <pre>{result.output || result.error}</pre>
        </div>
      )}
    </div>
  )
}

export default CodeChallenge
