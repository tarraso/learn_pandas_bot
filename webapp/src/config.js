/**
 * Application configuration
 * API_BASE will use environment variable in production, or default to localhost in development
 */

export const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default {
  API_BASE,
}
