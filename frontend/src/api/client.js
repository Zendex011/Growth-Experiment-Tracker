const client = {
  get: async (url, options = {}) => {
    let fullUrl = '/api' + url
    if (options.params) {
      const params = new URLSearchParams(options.params)
      fullUrl += '?' + params.toString()
    }
    const res = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
    return handleResponse(res)
  },
  post: async (url, data) => {
    const res = await fetch('/api' + url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    })
    return handleResponse(res)
  },
  patch: async (url, data) => {
    const res = await fetch('/api' + url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    })
    return handleResponse(res)
  },
  delete: async (url) => {
    const res = await fetch('/api' + url, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json'
      }
    })
    return handleResponse(res)
  }
}

async function handleResponse(res) {
  let data
  try {
    data = await res.json()
  } catch (e) {
    data = {}
  }
  
  if (!res.ok) {
    const errorBody = {
      message: data?.message || 'Something went wrong.',
      error: data?.error || 'UnknownError',
      status: res.status
    }
    return Promise.reject(errorBody)
  }
  
  return { data }
}

export default client
