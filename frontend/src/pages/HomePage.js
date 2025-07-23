import React, { useEffect, useState } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function HomePage() {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [search, setSearch] = useState('');
    const [filteredBooks, setFilteredBooks] = useState([]);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const loadData = () => {
        api.get('books/')
            .then(res => setBooks(res.data))
            .catch(() => setBooks([]));
        api.get('categories/')
            .then(res => setCategories(res.data))
            .catch(() => setCategories([]));
    };

    useEffect(() => {
        loadData();
    }, []);

    // Listen for login success to refresh page data
    useEffect(() => {
        const handleLoginSuccess = () => {
            loadData();
        };

        window.addEventListener('loginSuccess', handleLoginSuccess);
        return () => window.removeEventListener('loginSuccess', handleLoginSuccess);
    }, []);

    useEffect(() => {
        let filtered = books;
        if (selectedCategory) {
            filtered = filtered.filter(book => book.category === parseInt(selectedCategory));
        }
        if (search.trim()) {
            filtered = filtered.filter(book =>
                book.title.toLowerCase().includes(search.toLowerCase()) ||
                book.author.toLowerCase().includes(search.toLowerCase())
            );
        }
        setFilteredBooks(filtered.slice(0, 4));
    }, [books, selectedCategory, search]);

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
        } catch {
            setError('Could not borrow book.');
        }
    };

    return (
        <div>
            <h1 className="mb-4">Welcome to Literatrium Library</h1>
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
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <h2>Books</h2>
            <div className="row row-cols-1 row-cols-md-4 g-4 mb-5">
                {filteredBooks.map(book => (
                    <div className="col" key={book.id}>
                        <div className="card h-100" style={{ cursor: 'pointer', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                            <Link to={`/books/${book.id}`} style={{ textDecoration: 'none', color: 'inherit' }} className="d-block">
                                {book.cover_image && (
                                    <div style={{ width: '100%', aspectRatio: '1/1', background: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <img src={book.cover_image} className="card-img-top" alt={book.title} style={{ height: '320px', objectFit: 'fill' }} />
                                    </div>
                                )}
                                <div className="card-body p-3">
                                    <h5 className="card-title mb-1" style={{ fontSize: '1.1rem' }}>{book.title}</h5>
                                    <p className="card-text mb-2" style={{ fontSize: '0.95rem' }}>by {book.author}</p>
                                </div>
                            </Link>
                            <div className="card-footer bg-white border-0 p-3 pt-0">
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
                                    onClick={e => handleBorrow(book.id)}
                                >
                                    Borrow
                                </button>
                            )}

                            </div>
                        </div>
                    </div>
                ))}
                {filteredBooks.length === 0 && <div className="text-center text-muted">No books found.</div>}
            </div>
        </div>
    );
}

export default HomePage; 