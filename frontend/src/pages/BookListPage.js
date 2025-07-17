import React, { useEffect, useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

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

    useEffect(() => {
        setLoading(true);
        Promise.all([
            api.get('books/'),
            api.get('categories/')
        ]).then(([booksRes, catRes]) => {
            setBooks(booksRes.data);
            setCategories(catRes.data);
            setTotalPages(Math.ceil(booksRes.data.length / BOOKS_PER_PAGE));
            setLoading(false);
        }).catch(() => {
            setBooks([]);
            setCategories([]);
            setTotalPages(1);
            setLoading(false);
        });
    }, []);

    const filteredBooks = books.filter(book => {
        let match = true;
        if (selectedCategory) match = match && book.category === parseInt(selectedCategory);
        if (search.trim()) match = match && (
            book.title.toLowerCase().includes(search.toLowerCase()) ||
            book.author.toLowerCase().includes(search.toLowerCase())
        );
        return match;
    });

    const paginatedBooks = filteredBooks.slice((currentPage - 1) * BOOKS_PER_PAGE, currentPage * BOOKS_PER_PAGE);

    useEffect(() => {
        setTotalPages(Math.ceil(filteredBooks.length / BOOKS_PER_PAGE) || 1);
        setCurrentPage(1);
    }, [filteredBooks.length]);

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
        } catch (err) {
            setBorrowMsg(err.response?.data?.error || 'Could not borrow book.');
        }
    };

    return (
        <div>
            <h2>All Books</h2>
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
                    <div className="row row-cols-1 row-cols-md-4 g-4 mb-4">
                        {paginatedBooks.map(book => (
                            <div className="col" key={book.id}>
                                <div className="card h-100 book-card" onClick={() => navigate(`/books/${book.id}`)} style={{ cursor: 'pointer' }}>
                                    {book.cover_image && <img src={book.cover_image} className="card-img-top"  style={{ height: '320px', objectFit: 'fill' }} fill alt={book.title} />}
                                    <div className="card-body">
                                        <h5 className="card-title">{book.title}</h5>
                                        <p className="card-text">by {book.author}</p>
                                        {book.available_copies <= 0 ? (
                                            <button
                                                className="btn btn-secondary w-100 mt-2"
                                                disabled
                                            >
                                                Unavailable
                                            </button>
                                        ) : (
                                            <button
                                                className="btn btn-borrow w-100 mt-2"
                                                onClick={e => handleBorrow(e, book.id)}
                                            >
                                                Borrow
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {paginatedBooks.length === 0 && <div className="text-center text-muted">No books found.</div>}
                    </div>
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
                </>
            )}
        </div>
    );
}

export default BookListPage; 