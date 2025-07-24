import React, { useEffect, useState } from 'react';
import api from '../api';
import { useNavigate, useLocation } from 'react-router-dom';

const BOOKS_PER_PAGE = 4;

function BookListPage() {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [search, setSearch] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(true);
    const [borrowMsg, setBorrowMsg] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Check for parameters in URL
        const searchParams = new URLSearchParams(location.search);
        const categoryParam = searchParams.get('category');
        const typeParam = searchParams.get('type'); // 'top-rated' or 'most-popular'
        
        if (categoryParam) {
            setSelectedCategory(categoryParam);
        }

        setLoading(true);
        
        // Determine which API endpoint to use
        let booksEndpoint = 'books/';
        if (typeParam === 'top-rated') {
            booksEndpoint = 'books/top-rated/';
        } else if (typeParam === 'most-popular') {
            booksEndpoint = 'books/most-popular/';
        }
        
        Promise.all([
            api.get(booksEndpoint),
            api.get('categories/')
        ]).then(([booksRes, catRes]) => {
            setBooks(booksRes.data);
            setCategories(catRes.data);
            // Don't set totalPages here - let it be calculated by the filteredBooks effect
            setLoading(false);
        }).catch(() => {
            setBooks([]);
            setCategories([]);
            setTotalPages(1);
            setLoading(false);
        });
    }, [location.search]);

    const filteredBooks = books.filter(book => {
        let match = true;
        if (selectedCategory) {
            match = match && book.category === parseInt(selectedCategory);
        }
        if (search.trim()) {
            match = match && (
                book.title.toLowerCase().includes(search.toLowerCase()) ||
                book.author.toLowerCase().includes(search.toLowerCase())
            );
        }
        return match;
    });

    // Update pagination whenever filtered books change
    useEffect(() => {
        const newTotalPages = Math.ceil(filteredBooks.length / BOOKS_PER_PAGE) || 1;
        setTotalPages(newTotalPages);
        // Reset to page 1 if current page is beyond the new total
        if (currentPage > newTotalPages) {
            setCurrentPage(1);
        }
    }, [filteredBooks.length, currentPage]);

    // Also reset page when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [selectedCategory, search]);

    const paginatedBooks = filteredBooks.slice((currentPage - 1) * BOOKS_PER_PAGE, currentPage * BOOKS_PER_PAGE);

    const handlePageChange = (page) => {
        if (page >= 1 && page <= totalPages) {
            setCurrentPage(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const handleBorrow = async (e, bookId) => {
        e.stopPropagation();
        e.preventDefault();
        setBorrowMsg('');
        
        try {
            await api.post(`borrow/${bookId}/`);
            setBorrowMsg('Book borrowed successfully!');
            
            // Refresh books data to update available copies
            api.get('books/').then(booksRes => {
                setBooks(booksRes.data);
            }).catch(err => {
                console.error('Failed to refresh books data:', err);
            });
            
        } catch (err) {
            console.error('Borrow error:', err);
            
            if (err.response?.status === 400) {
                const errorMessage = err.response.data?.error || err.response.data?.message;
                
                if (errorMessage?.includes('already borrowed') || errorMessage?.includes('already have')) {
                    setBorrowMsg('You have already borrowed this book. Please return it before borrowing again.');
                } else if (errorMessage?.includes('No copies available') || errorMessage?.includes('not available')) {
                    setBorrowMsg('Sorry, this book is currently unavailable. All copies have been borrowed.');
                } else if (errorMessage?.includes('not logged in') || errorMessage?.includes('authentication')) {
                    setBorrowMsg('Please log in to borrow books.');
                } else {
                    setBorrowMsg(errorMessage || 'Could not borrow book. Please try again.');
                }
            } else if (err.response?.status === 401) {
                setBorrowMsg('Please log in to borrow books.');
            } else if (err.response?.status === 403) {
                setBorrowMsg('You do not have permission to borrow books.');
            } else {
                setBorrowMsg('Could not borrow book. Please check your connection and try again.');
            }
        }
    };

    // Get page title based on URL parameters
    const getPageTitle = () => {
        const searchParams = new URLSearchParams(location.search);
        const typeParam = searchParams.get('type');
        
        if (typeParam === 'top-rated') {
            return 'Top Rated Books';
        } else if (typeParam === 'most-popular') {
            return 'Most Popular Books';
        }
        return 'All Books';
    };

    return (
        <div>
            <h2>{getPageTitle()}</h2>
            <div className="row mb-4">
                <div className="col-md-6 mb-2">
                    <select className="form-select" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}>
                        <option value="">All Categories</option>
                        {categories.map(category => (
                            <option key={category.id} value={category.id}>{category.name}</option>
                        ))}
                    </select>
                </div>
                <div className="col-md-6 mb-2">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search by title or author..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>
            </div>
            {borrowMsg && <div className="alert alert-info">{borrowMsg}</div>}
            {loading ? (
                <div className="text-center my-5">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            ) : (
                <>
                    {/* Results Counter */}
                    <div className="d-flex justify-content-between align-items-center mb-3">
                        <p className="text-muted mb-0">
                            Showing {filteredBooks.length} book{filteredBooks.length !== 1 ? 's' : ''}
                            {selectedCategory && categories.find(cat => cat.id === parseInt(selectedCategory)) && 
                                ` in ${categories.find(cat => cat.id === parseInt(selectedCategory)).name}`
                            }
                            {search && ` matching "${search}"`}
                        </p>
                        {filteredBooks.length > BOOKS_PER_PAGE && (
                            <small className="text-muted">
                                Page {currentPage} of {totalPages}
                            </small>
                        )}
                    </div>
                    
                    <div className="row row-cols-1 row-cols-md-4 g-4 mb-4">
                        {paginatedBooks.map(book => (
                            <div className="col" key={book.id}>
                                <div className="card h-100 book-card" onClick={() => navigate(`/books/${book.id}`)} style={{ cursor: 'pointer' }}>
                                    {book.cover_image && <img src={book.cover_image} className="card-img-top"  style={{ height: '320px', objectFit: 'fill' }} fill alt={book.title} />}
                                    <div className="card-body">
                                        <h5 className="card-title">{book.title}</h5>
                                        <p className="card-text">by {book.author}</p>
                                        <p className="card-text">
                                            <small className="text-muted">
                                                Available: {book.available_copies}/{book.total_copies} copies
                                            </small>
                                        </p>
                                        {book.available_copies <= 0 ? (
                                            <button
                                                className="btn btn-secondary w-100 mt-2"
                                                disabled
                                                title="No copies available"
                                            >
                                                <i className="bi bi-x-circle"></i> Unavailable
                                            </button>
                                        ) : (
                                            <button
                                                className="btn btn-borrow w-100 mt-2"
                                                onClick={e => handleBorrow(e, book.id)}
                                                title={`Borrow this book (${book.available_copies} copies available)`}
                                            >
                                                <i className="bi bi-book"></i> Borrow
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {paginatedBooks.length === 0 && <div className="text-center text-muted">No books found.</div>}
                    </div>
                    {/* Pagination - only show if there are multiple pages */}
                    {totalPages > 1 && (
                        <nav aria-label="Book pagination">
                            <ul className="pagination justify-content-center">
                                <li className={`page-item${currentPage === 1 ? ' disabled' : ''}`}>
                                    <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>&laquo;</button>
                                </li>
                                {Array.from({ length: totalPages }, (_, i) => (
                                    <li key={i + 1} className={`page-item${currentPage === i + 1 ? ' active' : ''}`}>
                                        <button className="page-link" onClick={() => handlePageChange(i + 1)}>{i + 1}</button>
                                    </li>
                                ))}
                                <li className={`page-item${currentPage === totalPages ? ' disabled' : ''}`}>
                                    <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>&raquo;</button>
                                </li>
                            </ul>
                        </nav>
                    )}
                </>
            )}
        </div>
    );
}

export default BookListPage; 