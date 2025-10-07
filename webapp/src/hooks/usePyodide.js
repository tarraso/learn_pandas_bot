import { useState, useEffect, useRef } from 'react'

/**
 * Hook for loading and managing Pyodide instance
 * @returns {Object} { pyodide, loading, error, runPython }
 */
export function usePyodide() {
  const [pyodide, setPyodide] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [loadingPackages, setLoadingPackages] = useState(false)
  const packagesLoaded = useRef(new Set())

  useEffect(() => {
    const loadPyodideScript = async () => {
      try {
        setLoading(true)

        // Load Pyodide from CDN directly
        if (!window.loadPyodide) {
          const script = document.createElement('script')
          script.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js'
          script.async = true

          await new Promise((resolve, reject) => {
            script.onload = resolve
            script.onerror = () => reject(new Error('Failed to load Pyodide script'))
            document.head.appendChild(script)
          })
        }

        // Load Pyodide instance
        const pyodideInstance = await window.loadPyodide({
          indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/',
        })

        setPyodide(pyodideInstance)
        setError(null)
      } catch (err) {
        console.error('Failed to load Pyodide:', err)
        setError('Не удалось загрузить Python окружение')
      } finally {
        setLoading(false)
      }
    }

    loadPyodideScript()
  }, [])

  /**
   * Run Python code with Pyodide
   * @param {string} code - Python code to execute
   * @returns {Promise<{success: boolean, output?: string, error?: string}>}
   */
  const runPython = async (code) => {
    if (!pyodide) {
      return {
        success: false,
        error: 'Python окружение не загружено'
      }
    }

    try {
      // Load pandas and numpy if not already loaded
      if (!packagesLoaded.current.has('pandas')) {
        setLoadingPackages(true)
        await pyodide.loadPackage(['pandas', 'numpy'])
        packagesLoaded.current.add('pandas')
        setLoadingPackages(false)
      }

      // Redirect stdout to capture print statements
      await pyodide.runPythonAsync(`
import sys
from io import StringIO
sys.stdout = StringIO()
`)

      // Execute user code
      await pyodide.runPythonAsync(code)

      // Get output
      const output = await pyodide.runPythonAsync('sys.stdout.getvalue()')

      return {
        success: true,
        output: output || 'Код выполнен успешно (нет вывода)'
      }
    } catch (err) {
      // Extract error message
      let errorMsg = err.message || String(err)

      // Clean up Pyodide-specific error prefixes
      errorMsg = errorMsg.replace(/^PythonError: /, '')
      errorMsg = errorMsg.replace(/^Traceback.*?\n/, '')

      return {
        success: false,
        error: errorMsg
      }
    }
  }

  return {
    pyodide,
    loading,
    error,
    loadingPackages,
    runPython
  }
}
