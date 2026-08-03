// API Integration Helper
// This file contains functions to interact with the Flask API endpoints

const API_BASE_URL = '/api/v1';

// Helper function to make API calls
async function apiCall(endpoint, method = 'GET', data = null, token = null, retryOnUnauthorized = true) {
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    }
  };

  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }

  if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    if (response.status === 401 && token && retryOnUnauthorized) {
      const refreshedToken = await refreshAccessToken();
      if (refreshedToken) {
        return apiCall(endpoint, method, data, refreshedToken, false);
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || `HTTP Error: ${response.status}`);
    }

    if (response.status === 204) {
      return { success: true };
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showAlert(`Error: ${error.message}`, 'danger');
    return null;
  }
}

// ==================== AUTH API ====================

async function loginUser(email, password) {
  const data = await apiCall('/auth/login', 'POST', { email, password });
  if (data) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    showAlert('Login successful!', 'success');
    return data;
  }
  return null;
}

async function registerUser(name, email, password) {
  const data = await apiCall('/auth/register', 'POST', { name, email, password });
  if (data) {
    showAlert('Registration successful! Please log in.', 'success');
    return data;
  }
  return null;
}

async function logoutUser() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    await apiCall('/auth/logout', 'POST', { refresh_token: refreshToken });
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  showAlert('Logged out successfully', 'success');
}

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    const data = await apiCall('/auth/refresh', 'POST', { refresh_token: refreshToken });
    if (data) {
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    }
  }
  return null;
}

// ==================== TASK API ====================

async function getTasks(filters = {}, pagination = { page: 1, limit: 10 }) {
  const token = localStorage.getItem('access_token');
  const queryParams = new URLSearchParams({
    ...filters,
    ...pagination
  });
  
  const data = await apiCall(`/tasks?${queryParams}`, 'GET', null, token);
  return data;
}

async function getTaskById(taskId) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/${taskId}`, 'GET', null, token);
  return data;
}

async function createTask(taskData) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/tasks', 'POST', taskData, token);
  if (data) {
    showAlert('Task created successfully!', 'success');
  }
  return data;
}

async function updateTask(taskId, taskData) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/${taskId}`, 'PUT', taskData, token);
  if (data) {
    showAlert('Task updated successfully!', 'success');
  }
  return data;
}

async function updateTaskStatus(taskId, status) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/${taskId}/status`, 'PATCH', { status }, token);
  if (data) {
    showAlert('Task status updated!', 'success');
  }
  return data;
}

async function deleteTask(taskId) {
  if (!confirm('Are you sure you want to delete this task?')) {
    return null;
  }
  
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/${taskId}`, 'DELETE', null, token);
  if (data) {
    showAlert('Task deleted successfully!', 'success');
  }
  return data;
}

async function searchTasks(query) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/search?q=${encodeURIComponent(query)}`, 'GET', null, token);
  return data;
}

async function assignTask(taskId, userId) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/tasks/${taskId}/assign`, 'POST', { user_id: userId }, token);
  if (data) {
    showAlert('Task assigned successfully!', 'success');
  }
  return data;
}

// ==================== CATEGORY API ====================

async function getCategories() {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/categories', 'GET', null, token);
  return data;
}

async function createCategory(categoryData) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/categories', 'POST', categoryData, token);
  if (data) {
    showAlert('Category created successfully!', 'success');
  }
  return data;
}

async function deleteCategory(categoryId) {
  if (!confirm('Are you sure you want to delete this category?')) {
    return null;
  }
  
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/categories/${categoryId}`, 'DELETE', null, token);
  if (data) {
    showAlert('Category deleted successfully!', 'success');
  }
  return data;
}

async function updateCategory(categoryId, categoryData) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall(`/categories/${categoryId}`, 'PUT', categoryData, token);
  if (data) {
    showAlert('Category updated successfully!', 'success');
  }
  return data;
}

// ==================== USER API ====================

async function getProfile() {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/users/me', 'GET', null, token);
  return data;
}

async function updateProfile(userData) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/users/me', 'PUT', userData, token);
  if (data) {
    showAlert('Profile updated successfully!', 'success');
  }
  return data;
}

async function changePassword(currentPassword, newPassword) {
  const token = localStorage.getItem('access_token');
  const data = await apiCall('/users/me/password', 'PUT', {
    current_password: currentPassword,
    new_password: newPassword
  }, token);
  if (data) {
    showAlert('Password changed successfully!', 'success');
  }
  return data;
}

// ==================== HELPER FUNCTIONS ====================

// Get stored access token
function getAccessToken() {
  return localStorage.getItem('access_token');
}

// Check if user is authenticated
function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

// Expose API helpers under a single namespace to avoid global name collisions
window.API = {
  apiCall,
  loginUser,
  registerUser,
  logoutUser,
  refreshAccessToken,
  getTasks,
  getTaskById,
  createTask,
  updateTask,
  updateTaskStatus,
  deleteTask,
  searchTasks,
  assignTask,
  getCategories,
  createCategory,
  deleteCategory,
  updateCategory,
  getProfile,
  updateProfile,
  changePassword,
  getAccessToken,
  isAuthenticated
};

// Example usage in HTML forms
// Add this to your form submit handlers

/*
document.getElementById('createTaskForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const taskData = {
    title: document.getElementById('taskTitle').value,
    description: document.getElementById('taskDescription').value,
    priority: document.getElementById('taskPriority').value,
    category_id: document.getElementById('taskCategory').value,
    due_date: document.getElementById('taskDueDate').value
  };
  
  const result = await createTask(taskData);
  if (result) {
    e.target.reset();
    closeModal('newTaskModal');
    // Refresh tasks list
    loadTasks();
  }
});
*/
