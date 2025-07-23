import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function AnalyticsPage() {
    const [monthlyData, setMonthlyData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

    const yearOptions = [];
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 3; i++) {
        yearOptions.push(currentYear - i);
    }

    const fetchMonthlyData = async (year) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`http://127.0.0.1:5001/analytics/borrowed-per-month?year=${year}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                setMonthlyData(result.data);
            } else {
                setError(result.error || 'Failed to fetch analytics data');
            }
        } catch (err) {
            console.error('Error fetching analytics data:', err);
            setError('Unable to connect to analytics service. Please ensure the Flask server is running on port 5001.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMonthlyData(selectedYear);
    }, [selectedYear]);

    const handleYearChange = (event) => {
        const year = parseInt(event.target.value);
        setSelectedYear(year);
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: `Monthly Book Borrowings - ${selectedYear}`,
                font: {
                    size: 18,
                },
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Books Borrowed: ${context.parsed.y}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1,
                },
                title: {
                    display: true,
                    text: 'Number of Books Borrowed'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Month'
                }
            }
        },
    };

    const chartData = monthlyData ? {
        labels: monthlyData.labels,
        datasets: [
            {
                label: 'Books Borrowed',
                data: monthlyData.values,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(54, 162, 235, 0.8)',
                hoverBorderColor: 'rgba(54, 162, 235, 1)',
            },
        ],
    } : null;

    if (loading) {
        return (
            <div className="container mt-4">
                <div className="row justify-content-center">
                    <div className="col-md-8">
                        <div className="card">
                            <div className="card-body text-center">
                                <div className="spinner-border text-primary" role="status">
                                    <span className="visually-hidden">Loading...</span>
                                </div>
                                <p className="mt-3">Loading analytics data...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mt-4">
                <div className="row justify-content-center">
                    <div className="col-md-8">
                        <div className="card border-danger">
                            <div className="card-body">
                                <h5 className="card-title text-danger">
                                    <i className="bi bi-exclamation-triangle"></i> Error Loading Analytics
                                </h5>
                                <p className="card-text">{error}</p>
                                <div className="alert alert-info">
                                    <strong>To fix this:</strong>
                                    <ol className="mb-0 mt-2">
                                        <li>Make sure the Flask analytics server is running: <code>cd analytics && python app.py</code></li>
                                        <li>Verify the server is accessible at: <code>http://127.0.0.1:5001</code></li>
                                        <li>Check that PostgreSQL is configured and running</li>
                                    </ol>
                                </div>
                                <button 
                                    className="btn btn-primary" 
                                    onClick={() => fetchMonthlyData(selectedYear)}
                                >
                                    <i className="bi bi-arrow-clockwise"></i> Retry
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container mt-4">
            <div className="row">
                <div className="col-12">
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i className="bi bi-bar-chart"></i> Library Analytics
                        </h2>
                        <div>
                            <label htmlFor="yearSelect" className="form-label me-2">Year:</label>
                            <select 
                                id="yearSelect"
                                className="form-select d-inline-block"
                                style={{ width: 'auto' }}
                                value={selectedYear}
                                onChange={handleYearChange}
                            >
                                {yearOptions.map(year => (
                                    <option key={year} value={year}>{year}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {monthlyData && (
                <>
                    <div className="row mb-4">
                        <div className="col-md-3">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-primary">Total Borrowed</h5>
                                    <h3 className="text-primary">{monthlyData.total}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-success">Peak Month</h5>
                                    <h6 className="text-success">{monthlyData.peak_month || 'N/A'}</h6>
                                    <small className="text-muted">{monthlyData.peak_count} books</small>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-info">Average per Month</h5>
                                    <h6 className="text-info">
                                        {monthlyData.total > 0 ? Math.round(monthlyData.total / 12) : 0}
                                    </h6>
                                    <small className="text-muted">books/month</small>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-3">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-warning">Active Months</h5>
                                    <h6 className="text-warning">
                                        {monthlyData.values.filter(val => val > 0).length}
                                    </h6>
                                    <small className="text-muted">out of 12</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row">
                        <div className="col-12">
                            <div className="card">
                                <div className="card-body">
                                    <div style={{ height: '400px' }}>
                                        <Bar data={chartData} options={chartOptions} />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {monthlyData.error && (
                        <div className="row mt-3">
                            <div className="col-12">
                                <div className="alert alert-warning">
                                    <strong>Note:</strong> {monthlyData.note}
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
            <div className="row mt-4"></div>
        </div>
    );
}

export default AnalyticsPage;