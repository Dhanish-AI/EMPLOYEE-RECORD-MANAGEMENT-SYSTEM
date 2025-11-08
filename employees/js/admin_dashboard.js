(function () {
  const searchContainer = document.querySelector('[data-employee-search]');
  const searchInput = searchContainer?.querySelector('[data-employee-search-input]');
  const statusElement = searchContainer?.querySelector('.search-status');
  const tableBody = document.getElementById('employeeTableBody');
  const table = document.querySelector('[data-employee-table]');
  const endpoint = searchContainer?.dataset.searchEndpoint;

  const CHART_WIDTH = 420;
  const CHART_HEIGHT = 260;
  const DEVICE_PIXEL_RATIO = Math.min(window.devicePixelRatio || 1, 2);

  let debounceTimer;
  let activeController;

  function escapeHtml(value) {
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function setStatus(message) {
    if (!statusElement) return;
    statusElement.textContent = message;
  }

  function renderRows(results) {
    if (!tableBody) return;

    if (!results.length) {
      tableBody.innerHTML = '<tr class="no-results"><td colspan="7">No employees found.</td></tr>';
      return;
    }

    const rows = results
      .map((employee) => `
        <tr>
          <td>${escapeHtml(employee.employee_id)}</td>
          <td>${escapeHtml(employee.name)}</td>
          <td>${escapeHtml(employee.role || '')}</td>
          <td>${escapeHtml(employee.department || '')}</td>
          <td><span class="badge">${escapeHtml(employee.status || '')}</span></td>
          <td>${escapeHtml(employee.hire_date || '')}</td>
          <td class="row-actions">
            <a href="${employee.detail_url}">View</a>
            <a href="${employee.edit_url}">Edit</a>
            <a class="danger" href="${employee.delete_url}">Delete</a>
          </td>
        </tr>
      `)
      .join('');

    tableBody.innerHTML = rows;
  }

  async function performSearch(query) {
    if (!endpoint) return;

    if (activeController) {
      activeController.abort();
    }

    activeController = new AbortController();
    const signal = activeController.signal;

    const url = new URL(endpoint, window.location.origin);
    if (query) {
      url.searchParams.set('q', query);
    }

    setStatus('Searching…');
    table?.setAttribute('data-loading', 'true');

    try {
      const response = await fetch(url.toString(), { signal });
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      const data = await response.json();
      renderRows(data.results ?? []);
      setStatus(data.results?.length ? `${data.results.length} result(s)` : 'No employees found');
    } catch (error) {
      if (error.name === 'AbortError') {
        return;
      }
      console.error('Employee search failed', error);
      setStatus('Unable to fetch employees. Please try again.');
    } finally {
      table?.removeAttribute('data-loading');
    }
  }

  function handleSearchInput() {
    const query = searchInput?.value.trim() ?? '';

    if (debounceTimer) {
      window.clearTimeout(debounceTimer);
    }

    debounceTimer = window.setTimeout(() => {
      performSearch(query);
    }, 120);
  }

  function initSearch() {
    if (!searchContainer || !searchInput || !tableBody || !endpoint) {
      return;
    }

    searchInput.addEventListener('input', handleSearchInput);
  }

  function prepareCanvas(canvas) {
    if (!canvas) {
      return null;
    }

    canvas.style.width = `${CHART_WIDTH}px`;
    canvas.style.height = `${CHART_HEIGHT}px`;
    canvas.width = CHART_WIDTH * DEVICE_PIXEL_RATIO;
    canvas.height = CHART_HEIGHT * DEVICE_PIXEL_RATIO;
    return canvas;
  }

  function initCharts() {
    if (typeof Chart === 'undefined') {
      return;
    }

    const styles = window.getComputedStyle(document.documentElement);
    const isDark = (document.documentElement.dataset.theme || 'light') === 'dark';

    const lightText = styles.getPropertyValue('--chart-text-light').trim()
      || styles.getPropertyValue('--text-strong').trim()
      || '#0f172a';
    const darkText = styles.getPropertyValue('--chart-text-dark').trim()
      || styles.getPropertyValue('--text-strong').trim()
      || '#f8fafc';

    const textColor = isDark ? darkText : lightText;

    const gridColor = styles.getPropertyValue('--border-subtle').trim()
      || styles.getPropertyValue('--border').trim()
      || (isDark ? 'rgba(148, 163, 184, 0.25)' : 'rgba(148, 163, 184, 0.3)');

    const tooltipBg = styles.getPropertyValue('--tooltip-bg').trim()
      || styles.getPropertyValue(isDark ? '--surface' : '--surface-strong').trim()
      || (isDark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(241, 245, 249, 0.96)');

    const tooltipText = styles.getPropertyValue('--tooltip-text').trim()
      || styles.getPropertyValue(isDark ? '--text' : '--text-strong').trim()
      || (isDark ? '#f2f3f5ff' : '#0f172a');

    Chart.defaults.devicePixelRatio = DEVICE_PIXEL_RATIO;
    Chart.defaults.font.family = styles.getPropertyValue('--font-family-base').trim() || "'Poppins','Segoe UI',sans-serif";
    Chart.defaults.font.weight = '600';
    Chart.defaults.font.size = 14;
    Chart.defaults.color = textColor;

    const departmentDataElement = document.getElementById('department-chart-data');
    const statusDataElement = document.getElementById('status-chart-data');
    const departmentSalaryElement = document.getElementById('department-salary-chart-data');
    const departmentTenureElement = document.getElementById('department-tenure-chart-data');

    const departmentData = departmentDataElement ? JSON.parse(departmentDataElement.textContent) : null;
    const statusData = statusDataElement ? JSON.parse(statusDataElement.textContent) : null;
    const salaryData = departmentSalaryElement ? JSON.parse(departmentSalaryElement.textContent) : null;
    const tenureData = departmentTenureElement ? JSON.parse(departmentTenureElement.textContent) : null;

    const departmentCanvas = prepareCanvas(document.getElementById('departmentChart'));
    const statusCanvas = prepareCanvas(document.getElementById('statusChart'));
    const salaryCanvas = prepareCanvas(document.getElementById('salaryChart'));
    const tenureCanvas = prepareCanvas(document.getElementById('tenureChart'));

    const renderChart = (canvas, config) => {
      if (!canvas) {
        return;
      }

      const existing = Chart.getChart(canvas);
      if (existing) {
        existing.destroy();
      }

      return new Chart(canvas, config);
    };

    if (departmentCanvas && departmentData) {
      renderChart(departmentCanvas, {
        type: 'doughnut',
        data: {
          labels: departmentData.labels,
          datasets: [
            {
              label: 'Employees',
              data: departmentData.values,
              backgroundColor: ['#2f6fed', '#4d8dff', '#6fb3ff', '#92cbff', '#b5ddff', '#daf0ff'],
            },
          ],
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          interaction: {
            mode: 'nearest',
            intersect: true,
          },
          layout: {
            padding: {
              top: 12,
              right: 16,
              bottom: 12,
              left: 16,
            },
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                usePointStyle: true,
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
            tooltip: {
              backgroundColor: tooltipBg,
              bodyColor: tooltipText,
              titleColor: tooltipText,
              displayColors: false,
              callbacks: {
                title: () => '',
                label(context) {
                  const label = context.label || '';
                  const value = context.parsed || 0;
                  return `${label}: ${value}`;
                },
              },
            },
          },
        },
      });
    }

    if (statusCanvas && statusData) {
      renderChart(statusCanvas, {
        type: 'bar',
        data: {
          labels: statusData.labels,
          datasets: [
            {
              label: 'Employees',
              data: statusData.values,
              backgroundColor: '#2f6fed',
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          interaction: {
            mode: 'nearest',
            intersect: true,
          },
          layout: {
            padding: {
              top: 14,
              right: 16,
              bottom: 12,
              left: 16,
            },
          },
          scales: {
            x: {
              grid: {
                color: 'transparent',
              },
              ticks: {
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
            y: {
              beginAtZero: true,
              grid: {
                color: gridColor,
                drawBorder: false,
              },
              ticks: {
                precision: 0,
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
          },
          plugins: {
            tooltip: {
              backgroundColor: tooltipBg,
              bodyColor: tooltipText,
              titleColor: tooltipText,
              displayColors: false,
              callbacks: {
                title(context) {
                  return context?.[0]?.label ?? '';
                },
                label(context) {
                  const value = context.parsed?.y ?? context.parsed ?? 0;
                  return `${context.dataset.label}: ${value}`;
                },
              },
            },
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
          },
        },
      });
    }

    if (salaryCanvas && salaryData) {
      renderChart(salaryCanvas, {
        type: 'bar',
        data: {
          labels: salaryData.labels,
          datasets: [
            {
              label: 'Average Salary',
              data: salaryData.values,
              backgroundColor: '#4d8dff',
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          interaction: {
            mode: 'nearest',
            intersect: true,
          },
          layout: {
            padding: {
              top: 14,
              right: 16,
              bottom: 12,
              left: 16,
            },
          },
          scales: {
            x: {
              grid: {
                color: 'transparent',
              },
              ticks: {
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
            y: {
              beginAtZero: true,
              grid: {
                color: gridColor,
                drawBorder: false,
              },
              ticks: {
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
                callback(value) {
                  return `$${Number(value).toLocaleString()}`;
                },
              },
            },
          },
          plugins: {
            tooltip: {
              backgroundColor: tooltipBg,
              bodyColor: tooltipText,
              titleColor: tooltipText,
              displayColors: false,
              callbacks: {
                label(context) {
                  const value = context.parsed.y ?? 0;
                  return `${context.dataset.label}: $${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                },
                title(context) {
                  return context?.[0]?.label ?? '';
                },
              },
            },
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
          },
        },
      });
    }

    if (tenureCanvas && tenureData) {
      renderChart(tenureCanvas, {
        type: 'bar',
        data: {
          labels: tenureData.labels,
          datasets: [
            {
              label: 'Average Tenure',
              data: tenureData.values,
              backgroundColor: '#6fb3ff',
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          interaction: {
            mode: 'nearest',
            intersect: true,
          },
          layout: {
            padding: {
              top: 14,
              right: 16,
              bottom: 12,
              left: 16,
            },
          },
          scales: {
            x: {
              grid: {
                color: 'transparent',
              },
              ticks: {
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
            y: {
              beginAtZero: true,
              grid: {
                color: gridColor,
                drawBorder: false,
              },
              ticks: {
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
                callback(value) {
                  return `${Number(value).toFixed(1)} yrs`;
                },
              },
            },
          },
          plugins: {
            tooltip: {
              backgroundColor: tooltipBg,
              bodyColor: tooltipText,
              titleColor: tooltipText,
              displayColors: false,
              callbacks: {
                label(context) {
                  const value = context.parsed.y ?? 0;
                  return `${context.dataset.label}: ${value.toFixed(1)} yrs`;
                },
                title(context) {
                  return context?.[0]?.label ?? '';
                },
              },
            },
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                color: textColor,
                font: {
                  size: 13,
                  weight: '600',
                },
              },
            },
          },
        },
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initSearch();
  });

  window.addEventListener('load', () => {
    initCharts();
  });

  document.addEventListener('erms:theme-change', () => {
    initCharts();
  });
})();
