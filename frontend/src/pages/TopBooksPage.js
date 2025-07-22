import React, { useState, useEffect } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function TopBooksPage() {
    const [borrowingsData, setBorrowingsData] = useState(null);
    const [ratingsData, setRatingsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('borrowings');
    const [limit, setLimit] = useState(10);

    const fetchTopBooksByBorrowings = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5001/analytics/top-books-by-borrowings?limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                setBorrowingsData(result.data);
            } else {
                setError(result.error || 'Failed to fetch top books by borrowings');
            }
        } catch (err) {
            console.error('Error fetching borrowings data:', err);
            setError('Unable to connect to analytics service.');
        }
    };

    const fetchTopBooksByRatings = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5001/analytics/top-books-by-ratings?limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                setRatingsData(result.data);
            } else {
                setError(result.error || 'Failed to fetch top books by ratings');
            }
        } catch (err) {
            console.error('Error fetching ratings data:', err);
            setError('Unable to connect to analytics service.');
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            
            await Promise.all([
                fetchTopBooksByBorrowings(),
                fetchTopBooksByRatings()
            ]);
            
            setLoading(false);
        };

        fetchData();
    }, [limit]);

    const handleLimitChange = (event) => {
        setLimit(parseInt(event.target.value));
    };

    // Chart configurations
    const borrowingsChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: `Top ${limit} Books by Borrowings`,
                font: {
                    size: 16,
                },
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `Borrowings: ${context.parsed.y}`;
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
                    text: 'Number of Borrowings'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Books'
                },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            }
        },
    };

    const ratingsChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
            },
            title: {
                display: true,
                text: `Top ${limit} Books by Average Rating`,
                font: {
                    size: 16,
                },
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const book = ratingsData?.books[context.dataIndex];
                        return [
                            `${context.label}`,
                            `Rating: ${context.parsed}⭐`,
                            `Reviews: ${book?.review_count || 0}`
                        ];
                    }
                }
            }
        },
    };

    const borrowingsChartData = borrowingsData ? {
        labels: borrowingsData.books.map(book => 
            book.title.length > 20 ? book.title.substring(0, 20) + '...' : book.title
        ),
        datasets: [
            {
                label: 'Borrowings',
                data: borrowingsData.values,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(54, 162, 235, 0.8)',
            },
        ],
    } : null;

    const ratingsChartData = ratingsData ? {
        labels: ratingsData.books.map(book => 
            book.title.length > 15 ? book.title.substring(0, 15) + '...' : book.title
        ),
        datasets: [
            {
                label: 'Average Rating',
                data: ratingsData.values,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                ],
                hoverBackgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
                ],
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
                                <p className="mt-3">Loading top books data...</p>
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
                                    <i className="bi bi-exclamation-triangle"></i> Error Loading Top Books
                                </h5>
                                <p className="card-text">{error}</p>
                                <button 
                                    className="btn btn-primary" 
                                    onClick={() => window.location.reload()}
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
                            <i className="bi bi-star-fill"></i> Top Books
                        </h2>
                        <div>
                            <label htmlFor="limitSelect" className="form-label me-2">Show:</label>
                            <select 
                                id="limitSelect"
                                className="form-select d-inline-block"
                                style={{ width: 'auto' }}
                                value={limit}
                                onChange={handleLimitChange}
                            >
                                <option value={5}>Top 5</option>
                                <option value={10}>Top 10</option>
                                <option value={15}>Top 15</option>
                                <option value={20}>Top 20</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="row mb-4">
                <div className="col-12">
                    <ul className="nav nav-tabs" id="topBooksTab" role="tablist">
                        <li className="nav-item" role="presentation">
                            <button 
                                className={`nav-link ${activeTab === 'borrowings' ? 'active' : ''}`}
                                onClick={() => setActiveTab('borrowings')}
                                type="button"
                            >
                                <i className="bi bi-graph-up"></i> By Borrowings
                            </button>
                        </li>
                        <li className="nav-item" role="presentation">
                            <button 
                                className={`nav-link ${activeTab === 'ratings' ? 'active' : ''}`}
                                onClick={() => setActiveTab('ratings')}
                                type="button"
                            >
                                <i className="bi bi-star"></i> By Ratings
                            </button>
                        </li>
                    </ul>
                </div>
            </div>

            {/* Borrowings Tab Content */}
            {activeTab === 'borrowings' && borrowingsData && (
                <>
                    <div className="row mb-4">
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-primary">Total Borrowings</h5>
                                    <h3 className="text-primary">{borrowingsData.total_borrowings}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-success">Most Popular</h5>
                                    <h6 className="text-success">{borrowingsData.books[0]?.title || 'N/A'}</h6>
                                    <small className="text-muted">{borrowingsData.books[0]?.borrow_count || 0} borrowings</small>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-info">Average Borrowings</h5>
                                    <h6 className="text-info">
                                        {borrowingsData.books.length > 0 
                                            ? Math.round(borrowingsData.total_borrowings / borrowingsData.books.length)
                                            : 0
                                        }
                                    </h6>
                                    <small className="text-muted">per book</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row">
                        <div className="col-md-8">
                            <div className="card">
                                <div className="card-body">
                                    <div style={{ height: '400px' }}>
                                        <Bar data={borrowingsChartData} options={borrowingsChartOptions} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card">
                                <div className="card-header">
                                    <h6 className="mb-0">
                                        <i className="bi bi-list-ol"></i> Book Rankings
                                    </h6>
                                </div>
                                <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                    {borrowingsData.books.map((book, index) => (
                                        <div key={book.id} className="d-flex align-items-center mb-3">
                                            <div className="badge bg-primary me-3" style={{ fontSize: '14px' }}>
                                                #{index + 1}
                                            </div>
                                            <img 
                                                src={book.cover_image.startsWith('/') 
                                                    ? `http://127.0.0.1:8000${book.cover_image}` 
                                                    : book.cover_image
                                                }
                                                alt={book.title}
                                                className="me-3"
                                                style={{ width: '40px', height: '55px', objectFit: 'cover' }}
                                                onError={(e) => {
                                                    e.target.src = '/api/placeholder/40/55';
                                                }}
                                            />
                                            <div className="flex-grow-1">
                                                <div className="fw-bold" style={{ fontSize: '14px' }}>
                                                    {book.title}
                                                </div>
                                                <div className="text-muted small">
                                                    by {book.author}
                                                </div>
                                                <div className="text-primary small">
                                                    {book.borrow_count} borrowings
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Ratings Tab Content */}
            {activeTab === 'ratings' && ratingsData && (
                <>
                    <div className="row mb-4">
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-warning">Total Reviews</h5>
                                    <h3 className="text-warning">{ratingsData.total_reviews}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-success">Highest Rated</h5>
                                    <h6 className="text-success">{ratingsData.books[0]?.title || 'N/A'}</h6>
                                    <small className="text-muted">⭐{ratingsData.books[0]?.avg_rating || 0} avg rating</small>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card text-center">
                                <div className="card-body">
                                    <h5 className="card-title text-info">Overall Average</h5>
                                    <h6 className="text-info">⭐{ratingsData.avg_rating_overall}</h6>
                                    <small className="text-muted">across top books</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row">
                        <div className="col-md-8">
                            <div className="card">
                                <div className="card-body">
                                    <div style={{ height: '400px' }}>
                                        <Doughnut data={ratingsChartData} options={ratingsChartOptions} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="card">
                                <div className="card-header">
                                    <h6 className="mb-0">
                                        <i className="bi bi-star-fill"></i> Rating Rankings
                                    </h6>
                                </div>
                                <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                    {ratingsData.books.map((book, index) => (
                                        <div key={book.id} className="d-flex align-items-center mb-3">
                                            <div className="badge bg-warning me-3" style={{ fontSize: '14px' }}>
                                                #{index + 1}
                                            </div>
                                            <img 
                                                src={book.cover_image.startsWith('/') 
                                                    ? `http://127.0.0.1:8000${book.cover_image}` 
                                                    : book.cover_image
                                                }
                                                alt={book.title}
                                                className="me-3"
                                                style={{ width: '40px', height: '55px', objectFit: 'cover' }}
                                                onError={(e) => {
                                                    e.target.src = '/api/placeholder/40/55';
                                                }}
                                            />
                                            <div className="flex-grow-1">
                                                <div className="fw-bold" style={{ fontSize: '14px' }}>
                                                    {book.title}
                                                </div>
                                                <div className="text-muted small">
                                                    by {book.author}
                                                </div>
                                                <div className="text-warning small">
                                                    ⭐{book.avg_rating} ({book.review_count} reviews)
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Show message if no data */}
            {activeTab === 'ratings' && ratingsData && ratingsData.books.length === 0 && (
                <div className="row">
                    <div className="col-12">
                        <div className="alert alert-info">
                            <i className="bi bi-info-circle"></i> 
                            <strong> No books found with sufficient ratings.</strong> 
                            Books need at least 3 reviews to appear in the ratings ranking.
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TopBooksPage;
