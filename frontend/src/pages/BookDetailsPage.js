import React, { useEffect, useState } from 'react';
import api from '../api';
import { useParams } from 'react-router-dom';

function BookDetailsPage() {
    const { id } = useParams();
    const [book, setBook] = useState(null);
    const [reviews, setReviews] = useState([]);
    const [comment, setComment] = useState('');
    const [rating, setRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        api.get(`books/${id}/`).then(res => setBook(res.data));
        // Fetch reviews for this specific book
        api.get(`reviews/?book=${id}`).then(res => setReviews(res.data))
            .catch(err => {
                // Fallback: get all reviews and filter
                api.get('reviews/').then(res => {
                    const bookReviews = res.data.filter(r => r.book === parseInt(id));
                    setReviews(bookReviews);
                });
            });
    }, [id]);

    const handleReviewSubmit = async (e) => {
        e.preventDefault();
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in to review.');
            return;
        }
        if (rating === 0) {
            setError('Please select a rating before submitting your review.');
            return;
        }
        try {
            await api.post('reviews/', { book: parseInt(id), content: comment, rating });
            setSuccess('Review submitted!');
            setComment(''); setRating(0); setHoverRating(0);
            // Refresh reviews
            api.get(`reviews/?book=${id}`).then(res => setReviews(res.data))
                .catch(err => {
                    // Fallback: get all reviews and filter
                    api.get('reviews/').then(res => {
                        const bookReviews = res.data.filter(r => r.book === parseInt(id));
                        setReviews(bookReviews);
                    });
                });
        } catch (err) {
            console.error('Review submission error:', err);
            if (err.response?.status === 400) {
                setError('You have already reviewed this book. You can only submit one review per book.');
            } else {
                setError('Could not submit review. Please try again.');
            }
        }
    };

    if (!book) return <div className="text-center my-5"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div>;

    return (
        <div>
            <div className="row mb-4">
                <div className="col-md-4">
                    {book.cover_image && <img src={book.cover_image} alt={book.title} className="img-fluid rounded" />}
                </div>
                <div className="col-md-8">
                    <h2>{book.title}</h2>
                    <p><strong>Author:</strong> {book.author}</p>
                    <p><strong>Category:</strong> {book.category}</p>
                    <p><strong>Available Copies:</strong> {book.available_copies}</p>
                    <p><strong>Total Copies:</strong> {book.total_copies}</p>
                    <p><strong>ISBN:</strong> {book.isbn}</p>
                </div>
            </div>
            <h4>Reviews</h4>
            <div className="mb-4">
                {reviews.length === 0 && <p>No reviews yet.</p>}
                {reviews.map(r => (
                    <div className="card mb-2" key={r.id}>
                        <div className="card-body">
                            <div className="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>Rating:</strong> {r.rating}/5 ⭐<br />
                                    <small className="text-muted">By {r.user_name || 'Anonymous'}</small>
                                </div>
                                <small className="text-muted">
                                    {new Date(r.created_at).toLocaleDateString()}
                                </small>
                            </div>
                            <p className="mt-2 mb-0">{r.content}</p>
                        </div>
                    </div>
                ))}
            </div>
            <h5>Add a Review</h5>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form onSubmit={handleReviewSubmit} className="mb-4">
                <div className="mb-2">
                    <label className="form-label">Rating</label>
                    <div style={{ fontSize: '1.5rem' }}>
                        {[1, 2, 3, 4, 5].map(n => (
                            <span
                                key={n}
                                style={{ cursor: 'pointer', color: (hoverRating || rating) >= n ? '#ffc107' : '#e4e5e9' }}
                                onMouseEnter={() => setHoverRating(n)}
                                onMouseLeave={() => setHoverRating(0)}
                                onClick={() => setRating(n)}
                                role="button"
                                aria-label={`Rate ${n} star${n > 1 ? 's' : ''}`}
                            >
                                ★
                            </span>
                        ))}
                    </div>
                </div>
                <div className="mb-2">
                    <label className="form-label">Comment</label>
                    <textarea className="form-control" value={comment} onChange={e => setComment(e.target.value)} required />
                </div>
                <button type="submit" className="btn btn-primary">Submit Review</button>
            </form>
        </div>
    );
}

export default BookDetailsPage; 