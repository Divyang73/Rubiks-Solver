import axios from 'axios'

const BASE_URL = import.meta.env.VITE_BACKEND_URL || ''

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 130000
})

// Small async sleep used by retry backoff.
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Convert transport/library errors into stable categories for UI handling.
function classifyError(err) {
  const isTimeout = err?.code === 'ECONNABORTED'
  const hasNoResponse = !err?.response
  const status = err?.response?.status
  const category = isTimeout ? 'timeout' : hasNoResponse ? 'connection' : 'server'
  const retryable = isTimeout || hasNoResponse || status >= 500

  let message = 'Request failed'
  if (category === 'timeout') {
    message = 'The request timed out. Please retry or try a lighter scramble.'
  } else if (category === 'connection') {
    message = 'Could not connect to the server. Check connection and retry.'
  } else if (err?.response?.data?.detail?.message) {
    message = err.response.data.detail.message
  } else if (err?.response?.data?.detail?.error) {
    message = err.response.data.detail.error
  } else if (err?.message) {
    message = err.message
  }

  const enhanced = new Error(message)
  enhanced.category = category
  enhanced.retryable = retryable
  enhanced.status = status
  enhanced.raw = err
  return enhanced
}

async function requestWithRecovery(requestFn, options = {}) {
  const { maxRetries = 2, retryDelayMs = 500 } = options
  let attempts = 0

  while (true) {
    try {
      return await requestFn()
    } catch (err) {
      const normalized = classifyError(err)
      const canRetry = normalized.retryable && attempts < maxRetries
      if (!canRetry) {
        normalized.attempts = attempts + 1
        throw normalized
      }
      // Linear backoff keeps retries responsive but avoids immediate retry storms.
      attempts += 1
      await delay(retryDelayMs * attempts)
    }
  }
}

export async function healthCheck() {
  const { data } = await http.get('/api/')
  return data
}

export async function validateCube(cubeState) {
  const { data } = await requestWithRecovery(() => http.post('/api/validate', { cube_state: cubeState }))
  return data
}

export async function solveCube(payload) {
  const { data } = await requestWithRecovery(() => http.post('/api/solve', payload), {
    maxRetries: 1,
    retryDelayMs: 800
  })
  return data
}

export async function generateScramble(depth = 10) {
  const { data } = await requestWithRecovery(() => http.post('/api/scramble', { depth }))
  return data
}

export async function generateDifficultyScramble(difficulty) {
  const { data } = await requestWithRecovery(() =>
    http.post('/api/scramble/by-difficulty', { difficulty })
  )
  return data
}
