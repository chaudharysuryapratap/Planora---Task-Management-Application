// Utility Functions
function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  })[character]);
}

function showAlert(message, type = 'success') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type}`;
  alertDiv.textContent = message;
  
  const container = document.querySelector('.container');
  if (container) {
    container.insertBefore(alertDiv, container.firstChild);
  } else {
    // Fallback: insert at the beginning of body or use alert()
    const main = document.querySelector('main');
    if (main) {
      main.insertBefore(alertDiv, main.firstChild);
    } else {
      alert(message);
      return;
    }
  }
  
  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

let currentEditCategoryId = null;

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

function openEditCategoryModal(categoryId) {
  const card = document.querySelector(`[data-category-id="${categoryId}"]`);
  if (!card) return;

  currentEditCategoryId = categoryId;

  const name = card.querySelector('.category-name')?.textContent?.trim() || '';
  const color = card.getAttribute('data-category-color') || '#808080';

  document.getElementById('editCategoryName').value = name;
  document.getElementById('editCategoryColor').value = color;
  document.getElementById('editCategoryColorHex').value = color;

  showModal('editCategoryModal');
}

// Close modal when clicking outside of it
document.addEventListener('DOMContentLoaded', function() {
  const modals = document.querySelectorAll('.modal');
  
  modals.forEach(modal => {
    modal.addEventListener('click', function(event) {
      if (event.target === this) {
        this.classList.remove('active');
      }
    });

    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        modal.classList.remove('active');
      });
    }
  });

  // Form submission handlers
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Validate form
      const inputs = this.querySelectorAll('input[required], textarea[required], select[required]');
      let isValid = true;

      inputs.forEach(input => {
        if (!input.value.trim()) {
          input.style.borderColor = '#dc3545';
          isValid = false;
        } else {
          input.style.borderColor = '#9F2042';
        }
      });

      if (!isValid) {
        e.preventDefault();
        showAlert('Please fill in all required fields', 'warning');
      }
    });
  });

  // Handle edit category form submission
  const editCategoryForm = document.querySelector('#editCategoryModal form');
  if (editCategoryForm) {
    editCategoryForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      if (!currentEditCategoryId) return;

      const name = document.getElementById('editCategoryName').value.trim();
      const color = document.getElementById('editCategoryColor').value;

      const res = await API.updateCategory(currentEditCategoryId, { name, color });
      if (res) {
        const card = document.querySelector(`[data-category-id="${currentEditCategoryId}"]`);
        if (card) {
          const titleEl = card.querySelector('.category-name');
          if (titleEl) titleEl.textContent = name;
          card.setAttribute('data-category-color', color);
          card.style.borderLeftColor = color;
        }
        closeModal('editCategoryModal');
      }
    });
  }

  // Task filter
  const filterInputs = document.querySelectorAll('.filter-bar input, .filter-bar select');
  filterInputs.forEach(input => {
    input.addEventListener('change', filterTasks);
  });

  // Load categories for category page
  if (typeof loadCategories === 'function') {
    loadCategories();
  }

  // New category form submission
  const newCategoryForm = document.querySelector('#newCategoryModal form');
  if (newCategoryForm) {
    newCategoryForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const name = document.getElementById('categoryName').value.trim();
      const color = document.getElementById('categoryColor').value;
      const res = await API.createCategory({ name, color });
      if (res) {
        closeModal('newCategoryModal');
        this.reset();
        if (typeof loadCategories === 'function') loadCategories();
      }
    });
  }
});

// Filter tasks
function filterTasks() {
  const tasks = document.querySelectorAll('.task-card');
  const statusFilter = document.querySelector('[data-filter="status"]')?.value || '';
  const priorityFilter = document.querySelector('[data-filter="priority"]')?.value || '';
  const searchFilter = document.querySelector('[data-filter="search"]')?.value?.toLowerCase() || '';

  tasks.forEach(task => {
    let shouldShow = true;

    if (statusFilter && !task.classList.contains(statusFilter)) {
      shouldShow = false;
    }

    if (priorityFilter) {
      const priorityBadge = task.querySelector('.task-priority');
      if (!priorityBadge || !priorityBadge.textContent.toLowerCase().includes(priorityFilter)) {
        shouldShow = false;
      }
    }

    if (searchFilter) {
      const title = task.querySelector('h4')?.textContent?.toLowerCase() || '';
      const description = task.querySelector('p')?.textContent?.toLowerCase() || '';
      if (!title.includes(searchFilter) && !description.includes(searchFilter)) {
        shouldShow = false;
      }
    }

    task.style.display = shouldShow ? 'block' : 'none';
  });
}

// Toggle task completion
function toggleTaskCompletion(taskId) {
  const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
  if (taskCard) {
    taskCard.classList.toggle('completed');
  }
}

// Server-backed toggle: mark task as done or revert to todo
async function toggleTaskCompletionServer(taskId) {
  const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
  if (!taskCard) return;

  // Determine current status (fallback to 'todo')
  const statusSpan = taskCard.querySelector('.task-status');
  let currentStatus = 'todo';
  if (statusSpan) {
    // class may contain status like 'todo', 'in_progress', 'done'
    const classes = statusSpan.className.split(/\s+/);
    currentStatus = classes.find(c => ['todo','in_progress','done','archived'].includes(c)) || 'todo';
  }

  const newStatus = currentStatus === 'done' ? 'todo' : 'done';

  const res = await API.updateTaskStatus(taskId, newStatus);
  if (res) {
    // update UI classes and text
    taskCard.classList.toggle('completed', newStatus === 'done');
    if (statusSpan) {
      // remove old status classes
      statusSpan.classList.remove('todo','in_progress','done','archived');
      statusSpan.classList.add(newStatus);
      statusSpan.textContent = newStatus.replace('_',' ').toUpperCase();
    }
    updateStats();
    if (typeof loadTasks === 'function') loadTasks();
  }
}

// Delete task with confirmation
function deleteTask(taskId) {
  if (confirm('Are you sure you want to delete this task?')) {
    // API call would go here
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) {
      taskCard.remove();
      showAlert('Task deleted successfully', 'success');
    }
  }
}

// Server-backed deletion: calls API.deleteTask then updates UI
async function deleteTaskServer(taskId) {
  const res = await API.deleteTask(taskId);
  if (res) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) taskCard.remove();
    // refresh stats and lists
    updateStats();
    if (typeof loadTasks === 'function') loadTasks();
  }
}

// Delete category with confirmation
function deleteCategory(categoryId) {
  if (confirm('Are you sure you want to delete this category?')) {
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);
    if (categoryCard) {
      categoryCard.remove();
      showAlert('Category deleted successfully', 'success');
    }
  }
}

// Server-backed category delete helper
async function deleteCategoryServer(categoryId) {
  const res = await API.deleteCategory(categoryId);
  if (res) {
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);
    if (categoryCard) categoryCard.remove();
    showAlert('Category deleted successfully', 'success');
    if (typeof loadCategories === 'function') loadCategories();
  }
}

// Format date
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

// Get status badge color
function getStatusColor(status) {
  const colors = {
    'todo': 'todo',
    'in_progress': 'in_progress',
    'done': 'done',
    'archived': 'archived'
  };
  return colors[status] || 'todo';
}

// Get priority color
function getPriorityColor(priority) {
  const colors = {
    'low': 'low',
    'medium': 'medium',
    'high': 'high'
  };
  return colors[priority] || 'medium';
}

// Count tasks by status
function getTaskStats() {
  const allTasks = document.querySelectorAll('.task-card');
  const stats = {
    total: allTasks.length,
    todo: 0,
    in_progress: 0,
    done: 0,
    completed: 0
  };

  allTasks.forEach(task => {
    stats.todo += task.classList.contains('todo') ? 1 : 0;
    stats.in_progress += task.classList.contains('in_progress') ? 1 : 0;
    stats.done += task.classList.contains('done') ? 1 : 0;
    stats.completed += task.classList.contains('completed') ? 1 : 0;
  });

  return stats;
}

// Update task stats display
function updateStats() {
  const stats = getTaskStats();
  const totalStat = document.querySelector('[data-stat="total"]');
  const todoStat = document.querySelector('[data-stat="todo"]');
  const inProgressStat = document.querySelector('[data-stat="in_progress"]');
  const doneStat = document.querySelector('[data-stat="done"]');

  if (totalStat) totalStat.textContent = stats.total;
  if (todoStat) todoStat.textContent = stats.todo;
  if (inProgressStat) inProgressStat.textContent = stats.in_progress;
  if (doneStat) doneStat.textContent = stats.done;
}

// Search functionality
function searchTasks(query) {
  const tasks = document.querySelectorAll('.task-card');
  const searchQuery = query.toLowerCase();

  tasks.forEach(task => {
    const title = task.querySelector('h4')?.textContent?.toLowerCase() || '';
    const description = task.querySelector('p')?.textContent?.toLowerCase() || '';
    
    const matches = title.includes(searchQuery) || description.includes(searchQuery);
    task.style.display = matches ? 'block' : 'none';
  });
}

// Sort tasks
function sortTasks(sortBy) {
  const tasksContainer = document.querySelector('.grid, .task-list');
  if (!tasksContainer) return;

  const tasks = Array.from(tasksContainer.querySelectorAll('.task-card'));
  
  tasks.sort((a, b) => {
    switch(sortBy) {
      case 'date-asc':
        return new Date(a.dataset.dueDate) - new Date(b.dataset.dueDate);
      case 'date-desc':
        return new Date(b.dataset.dueDate) - new Date(a.dataset.dueDate);
      case 'priority-high':
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        const priorityA = priorityOrder[a.querySelector('.task-priority')?.textContent?.toLowerCase()] || 0;
        const priorityB = priorityOrder[b.querySelector('.task-priority')?.textContent?.toLowerCase()] || 0;
        return priorityB - priorityA;
      case 'title-asc':
        return a.querySelector('h4')?.textContent?.localeCompare(b.querySelector('h4')?.textContent);
      default:
        return 0;
    }
  });

  // Re-append sorted tasks
  tasks.forEach(task => {
    tasksContainer.appendChild(task);
  });
}

// Character counter for textarea
function initCharCounter() {
  const textareas = document.querySelectorAll('textarea[maxlength]');
  textareas.forEach(textarea => {
    const maxLength = textarea.getAttribute('maxlength');
    const counter = document.createElement('small');
    counter.className = 'char-counter';
    counter.style.display = 'block';
    counter.style.marginTop = '0.5rem';
    counter.style.color = 'var(--medium-purple)';
    counter.textContent = `0 / ${maxLength}`;
    textarea.parentNode.insertBefore(counter, textarea.nextSibling);

    textarea.addEventListener('input', function() {
      counter.textContent = `${this.value.length} / ${maxLength}`;
    });
  });
}

// Password strength indicator
function initPasswordStrengthCheck() {
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  passwordInputs.forEach(input => {
    input.addEventListener('input', function() {
      const strength = calculatePasswordStrength(this.value);
      // You can add visual feedback here
      console.log('Password strength:', strength);
    });
  });
}

function calculatePasswordStrength(password) {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
  if (password.match(/[0-9]/)) strength++;
  if (password.match(/[^a-zA-Z0-9]/)) strength++;
  
  const levels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
  return levels[strength] || 'Weak';
}

// Categories renderer
function createCategoryCard(category) {
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.categoryId = category.id;
  card.dataset.categoryColor = category.color;
  card.style.borderLeft = `4px solid ${category.color}`;

  const tasksCount = category.tasks_count || 0;

  card.innerHTML = `
    <div class="card-header">
      <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 1.5rem;">📁</span>
        <span class="category-name">${escapeHTML(category.name)}</span>
      </h3>
    </div>
    <p>${escapeHTML(category.description || '')}</p>
    <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
      <button class="btn btn-primary btn-small" onclick="openEditCategoryModal('${category.id}')">Edit</button>
      <button class="btn btn-danger btn-small" onclick="deleteCategoryServer('${category.id}')">Delete</button>
    </div>
    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #9F2042;">
      <small style="color: #7B0D1E;">📊 ${tasksCount} tasks</small>
    </div>
  `;

  return card;
}

async function loadCategories() {
  const grid = document.getElementById('categoriesGrid');
  if (!grid) return;

  grid.innerHTML = '<div class="card" style="text-align: center; padding: 2rem;">Loading categories…</div>';

  const res = await API.getCategories();
  const categories = res?.data || [];

  grid.innerHTML = '';
  if (!categories.length) {
    grid.innerHTML = '<div class="card" style="text-align: center; padding: 2rem;">No categories found.</div>';
    return;
  }

  categories.forEach(category => {
    grid.appendChild(createCategoryCard(category));
  });
}

// Confirmation dialog
function confirmAction(message = 'Are you sure?') {
  return confirm(message);
}

// Export data
function exportTasksAsJSON() {
  const tasks = [];
  document.querySelectorAll('.task-card').forEach(task => {
    tasks.push({
      title: task.querySelector('h4')?.textContent,
      description: task.querySelector('p')?.textContent,
      status: task.className.match(/\b(todo|in_progress|done)\b/)?.[0],
      priority: task.querySelector('.task-priority')?.textContent?.toLowerCase(),
      dueDate: task.dataset.dueDate
    });
  });

  const dataStr = JSON.stringify(tasks, null, 2);
  const dataBlob = new Blob([dataStr], {type: 'application/json'});
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `tasks_${new Date().toISOString().split('T')[0]}.json`;
  link.click();
}

// Initialize on page load
window.addEventListener('load', function() {
  initCharCounter();
  initPasswordStrengthCheck();
  updateStats();
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
