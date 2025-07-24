import React, { useEffect, useState } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function HomePage() {
    const [stats, setStats] = useState(null);
    const [topRatedBooks, setTopRatedBooks] = useState([]);
    const [mostBorrowedBooks, setMostBorrowedBooks] = useState([]);
    const [categoriesWithBooks, setCategoriesWithBooks] = useState([]);
    const [selectedCategoryId, setSelectedCategoryId] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(true);

    // Auto-clear messages after 3 seconds
    useEffect(() => {
        if (error || success) {
            const timer = setTimeout(() => {
                setError('');
                setSuccess('');
            }, 3000);
            
            return () => clearTimeout(timer);
        }
    }, [error, success]);

    const loadHomeData = async () => {
        try {
            setLoading(true);
            
            // Fetch all data in parallel
            const [statsRes, topRatedRes, mostBorrowedRes, categoriesRes] = await Promise.all([
                api.get('home/stats/'),
                api.get('home/top-rated/'),
                api.get('home/most-borrowed/'),
                api.get('home/categories-with-books/')
            ]);
            
            setStats(statsRes.data);
            setTopRatedBooks(topRatedRes.data);
            setMostBorrowedBooks(mostBorrowedRes.data);
            setCategoriesWithBooks(categoriesRes.data);
        } catch (err) {
            console.error('Failed to load home data:', err);
            setError('Failed to load data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHomeData();
    }, []);

    // Listen for login success to refresh page data
    useEffect(() => {
        const handleLoginSuccess = () => {
            loadHomeData();
        };

        window.addEventListener('loginSuccess', handleLoginSuccess);
        return () => window.removeEventListener('loginSuccess', handleLoginSuccess);
    }, []);

    const handleBorrow = async (bookId) => {
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in to borrow books.');
            return;
        }
        try {
            await api.post(`borrow/${bookId}/`);
            setSuccess('Book borrowed successfully!');
            // Refresh data to update available copies
            loadHomeData();
        } catch (err) {
            console.error('Borrow error:', err);
            
            if (err.response?.status === 400) {
                const errorMessage = err.response.data?.error;
                
                if (errorMessage?.includes('already borrowed')) {
                    setError('You have already borrowed this book and haven\'t returned it yet.');
                } else if (errorMessage?.includes('No copies available')) {
                    setError('Sorry, this book is currently unavailable. All copies are borrowed.');
                } else {
                    setError('Unable to borrow this book. Please try again later.');
                }
            } else if (err.response?.status === 404) {
                setError('Book not found. Please refresh the page and try again.');
            } else {
                setError('Could not borrow book. Please check your connection and try again.');
            }
        }
    };

    const scrollToPopular = () => {
        const popularSection = document.getElementById('popular-section');
        if (popularSection) {
            popularSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const scrollToCategories = () => {
        const categoriesSection = document.getElementById('categories-section');
        if (categoriesSection) {
            categoriesSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const renderStars = (rating) => {
        return (
            <span style={{ color: '#ffc107', fontSize: '0.9rem' }}>
                {[1, 2, 3, 4, 5].map(star => (
                    <span key={star}>
                        {star <= rating ? '★' : '☆'}
                    </span>
                ))}
            </span>
        );
    };

    const BookCard = ({ book, showRating = false, showBorrowCount = false }) => (
        <div className="col-md-3 mb-4">
            <div className="card h-100" style={{ 
                borderRadius: '0.75rem', 
                boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                transition: 'transform 0.2s, box-shadow 0.2s'
            }}>
                <Link to={`/books/${book.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    {book.cover_image && (
                        <div style={{ 
                            height: '240px', 
                            overflow: 'hidden', 
                            borderRadius: '0.75rem 0.75rem 0 0' 
                        }}>
                            <img 
                                src={book.cover_image} 
                                className="card-img-top" 
                                alt={book.title}
                                style={{ 
                                    height: '240px', 
                                    width: '100%', 
                                    objectFit: 'fill',
                                    transition: 'transform 0.2s'
                                }}
                                onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                                onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                            />
                        </div>
                    )}
                    <div className="card-body p-3">
                        <h6 className="card-title mb-1 fw-bold" style={{ fontSize: '0.95rem' }}>
                            {book.title.length > 30 ? book.title.substring(0, 30) + '...' : book.title}
                        </h6>
                        <p className="card-text mb-2 text-muted" style={{ fontSize: '0.85rem' }}>
                            by {book.author.length > 20 ? book.author.substring(0, 20) + '...' : book.author}
                        </p>
                        {showRating && book.average_rating && (
                            <div className="mb-2">
                                {renderStars(book.average_rating)}
                                <small className="text-muted ms-1">({book.review_count} reviews)</small>
                            </div>
                        )}
                        {showBorrowCount && (
                            <div className="mb-2">
                                <small className="text-primary">
                                    <i className="bi bi-graph-up"></i> {book.borrow_count} times borrowed
                                </small>
                            </div>
                        )}
                    </div>
                </Link>
                <div className="card-footer bg-white border-0 p-3 pt-0">
                    {book.available_copies <= 0 ? (
                        <button className="btn btn-secondary w-100 btn-sm" disabled>
                            Unavailable
                        </button>
                    ) : (
                        <button
                            className="btn btn-primary w-100 btn-sm"
                            onClick={() => handleBorrow(book.id)}
                        >
                            Borrow Book
                        </button>
                    )}
                </div>
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="text-center my-5">
                <div className="spinner-border" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-3">Loading library dashboard...</p>
            </div>
        );
    }

    return (
        <div>
            {/* Hero Section */}
            <div className="bg-primary text-white rounded-4 p-4 mb-4" style={{ 
                background: 'linear-gradient(135deg, #0d6efd 0%, #0056b3 100%)' 
            }}>
                <div className="row align-items-center">
                    <div className="col-md-8">
                        <h1 className="display-5 fw-bold mb-3">Welcome to Literatrium Library</h1>
                        <p className="lead mb-3">Discover your next favorite book from our extensive collection</p>
                        <div className="d-flex flex-wrap gap-2">
                            <Link to="/books" className="btn btn-light btn-lg">
                                <i className="bi bi-book"></i> Browse All Books
                            </Link>
                            <button 
                                onClick={scrollToPopular}
                                className="btn btn-outline-light"
                            >
                                <i className="bi bi-graph-up"></i> Most Popular
                            </button>
                            <button 
                                onClick={scrollToCategories}
                                className="btn btn-outline-light"
                            >
                                <i className="bi bi-collection"></i> Browse Categories
                            </button>
                        </div>
                    </div>
                    <div className="col-md-4">
                        {stats && (
                            <div className="row text-center">
                                <div className="col-6 mb-2">
                                    <h3 className="fw-bold">{stats.total_books}</h3>
                                    <small>Total Books</small>
                                </div>
                                <div className="col-6 mb-2">
                                    <h3 className="fw-bold">{stats.total_categories}</h3>
                                    <small>Categories</small>
                                </div>
                                <div className="col-6">
                                    <h3 className="fw-bold">{stats.total_borrowings}</h3>
                                    <small>Total Borrowings</small>
                                </div>
                                <div className="col-6">
                                    <h3 className="fw-bold">{stats.average_rating}</h3>
                                    <small>Avg Rating</small>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Messages */}
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            {/* Top Rated Books Section */}
            <section className="mb-5">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2 className="h3 fw-bold text-primary">
                        <i className="bi bi-star-fill me-2"></i>
                        Top Rated Books
                    </h2>
                    <Link to="/books?type=top-rated" className="btn btn-outline-primary btn-sm">
                        View All <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                {topRatedBooks.length > 0 ? (
                    <div className="row">
                        {topRatedBooks.slice(0, 4).map(book => (
                            <BookCard key={book.id} book={book} showRating={true} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center text-muted py-4">
                        <i className="bi bi-star display-1 text-muted"></i>
                        <p>No rated books yet. Be the first to rate a book!</p>
                    </div>
                )}
            </section>

            {/* Most Borrowed Books Section */}
            <section className="mb-5" id="popular-section">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2 className="h3 fw-bold text-success">
                        <i className="bi bi-graph-up me-2"></i>
                        Most Popular Books
                    </h2>
                    <Link to="/books?type=most-popular" className="btn btn-outline-success btn-sm">
                        View All <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                {mostBorrowedBooks.length > 0 ? (
                    <div className="row">
                        {mostBorrowedBooks.slice(0, 4).map(book => (
                            <BookCard key={book.id} book={book} showBorrowCount={true} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center text-muted py-4">
                        <i className="bi bi-graph-up display-1 text-muted"></i>
                        <p>No borrowing data yet. Start borrowing books!</p>
                    </div>
                )}
            </section>

            {/* Categories Section */}
            <section className="mb-5" id="categories-section">
                <h2 className="h3 fw-bold text-info mb-4">
                    <i className="bi bi-collection me-2"></i>
                    Browse by Categories
                </h2>
                
                {/* Category Selection */}
                <div className="card mb-4" style={{ 
                    borderRadius: '0.75rem', 
                    boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
                }}>
                    <div className="card-body p-4">
                        <div className="text-center mb-3">
                            <h5 className="card-title mb-2">
                                <i className="bi bi-grid-3x3-gap me-2 text-info"></i>
                                Select a Category
                            </h5>
                            <p className="card-text text-muted mb-3">
                                Choose from {categoriesWithBooks.length} categories to discover books in your favorite genres
                            </p>
                        </div>
                        
                        {/* Category Buttons */}
                        <div className="d-flex flex-wrap justify-content-center gap-3 mb-4">
                            <button
                                className={`btn ${selectedCategoryId === '' ? 'btn-info' : 'btn-outline-info'}`}
                                onClick={() => setSelectedCategoryId('')}
                                style={{ minWidth: '120px' }}
                            >
                                <i className="bi bi-collection me-2"></i>
                                All Categories
                            </button>
                            
                            {categoriesWithBooks.map(category => (
                                <button
                                    key={category.id}
                                    className={`btn ${
                                        selectedCategoryId === category.id.toString() ? 'btn-info' : 'btn-outline-info'
                                    }`}
                                    onClick={() => setSelectedCategoryId(category.id.toString())}
                                    style={{ minWidth: '100px' }}
                                >
                                    {category.name}
                                    <span className="badge bg-light text-dark ms-2">{category.total_books}</span>
                                </button>
                            ))}
                        </div>
                        
                        {/* Quick Stats */}
                        <div className="text-center">
                            <small className="text-muted">
                                <i className="bi bi-info-circle me-1"></i>
                                {categoriesWithBooks.reduce((total, cat) => total + cat.total_books, 0)} books 
                                across {categoriesWithBooks.length} categories
                            </small>
                        </div>
                    </div>
                </div>

                {/* Display Selected Category Books or Clean Message */}
                {selectedCategoryId ? (
                    // Show selected category books
                    categoriesWithBooks
                        .filter(category => category.id === parseInt(selectedCategoryId))
                        .map(category => (
                            <div key={category.id} className="mb-4">
                                <div className="d-flex justify-content-between align-items-center mb-4">
                                    <h3 className="h4 text-dark mb-0">
                                        <i className="bi bi-bookmark-fill me-2 text-info"></i>
                                        {category.name} Collection
                                    </h3>
                                    <div className="d-flex gap-2">
                                        <span className="badge bg-info fs-6 px-3 py-2">
                                            {category.total_books} books available
                                        </span>
                                        <Link 
                                            to={`/books?category=${category.id}`} 
                                            className="btn btn-info btn-sm"
                                        >
                                            View All <i className="bi bi-arrow-right"></i>
                                        </Link>
                                    </div>
                                </div>
                                {category.books.length > 0 ? (
                                    <div className="row">
                                        {category.books.map(book => (
                                            <BookCard key={book.id} book={book} />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="alert alert-info border-0" style={{ backgroundColor: '#e7f3ff' }}>
                                        <div className="d-flex align-items-center">
                                            <i className="bi bi-info-circle me-3 text-info" style={{ fontSize: '1.5rem' }}></i>
                                            <div>
                                                <h6 className="mb-1">No books displayed</h6>
                                                <p className="mb-0 text-muted">Books in this category are available but not shown in the preview. Click "View All" to see the complete collection.</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                ) : (
                    // Clean welcome message when no category is selected
                    <div className="text-center py-4">
                        <div className="mb-4">
                            <i className="bi bi-collection text-info mb-3" style={{ fontSize: '3rem' }}></i>
                            <h4 className="text-info mb-3">Explore Our Book Categories</h4>
                            <p className="text-muted mb-0" style={{ maxWidth: '500px', margin: '0 auto' }}>
                                Select any category above to discover curated books in that genre. 
                                Each category showcases the best titles we have to offer.
                            </p>
                        </div>
                    </div>
                )}
            </section>

            {/* Call to Action */}
            <div className="bg-light rounded-4 p-4 text-center mb-5">
                <h3 className="fw-bold mb-3">Ready to Start Reading?</h3>
                <p className="text-muted mb-3">
                    Join thousands of readers and discover your next favorite book today!
                </p>
                <div className="d-flex justify-content-center gap-3">
                    <Link to="/books" className="btn btn-primary btn-lg">
                        <i className="bi bi-book"></i> Browse Books
                    </Link>
                    <Link to="/signup" className="btn btn-outline-primary btn-lg">
                        <i className="bi bi-person-plus"></i> Join Library
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default HomePage; 