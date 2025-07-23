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
    const [userReview, setUserReview] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [currentUsername, setCurrentUsername] = useState(null);
    const [currentUserId, setCurrentUserId] = useState(null);

    useEffect(() => {
        api.get(`books/${id}/`).then(res => setBook(res.data));
        
        // Get current user's info once
        const token = localStorage.getItem('token');
        console.log('=== USER AUTHENTICATION DEBUG ===');
        console.log('Token from localStorage:', token ? 'EXISTS' : 'NOT_FOUND');
        
        if (token) {
            console.log('Making profile API call...');
            api.get('profile/').then(profileRes => {
                console.log('Profile API response:', profileRes);
                console.log('Profile data:', profileRes.data);
                
                const userData = profileRes.data.user;
                console.log('User data from profile:', userData);
                
                if (userData) {
                    console.log('Setting user info:', {
                        id: userData.id,
                        username: userData.username
                    });
                    setCurrentUsername(userData.username);
                    setCurrentUserId(userData.id);
                    
                    // Now fetch reviews with user info available
                    loadReviews(userData.id, userData.username);
                } else {
                    console.error('No user data in profile response');
                    loadReviews(null, null);
                }
            }).catch(err => {
                console.error('Failed to get user profile:', err);
                console.error('Error details:', err.response);
                loadReviews(null, null);
            });
        } else {
            console.log('No token found - user not logged in');
            loadReviews(null, null);
        }
    }, [id]);

    const loadReviews = (userId, username) => {
        // Fetch reviews for this specific book
        api.get(`reviews/?book=${id}`).then(res => {
            console.log('=== REVIEW DEBUGGING ===');
            console.log('Book ID:', id);
            console.log('Current User ID:', userId);
            console.log('Current Username:', username);
            console.log('Raw API response:', res.data);
            
            // Debug each review structure
            res.data.forEach((review, index) => {
                console.log(`Review ${index + 1} structure:`, {
                    id: review.id,
                    user: review.user,
                    user_name: review.user_name,
                    book: review.book,
                    content: review.content?.substring(0, 30) + '...',
                    rating: review.rating,
                    created_at: review.created_at
                });
            });
            
            setReviews(res.data);
            
            // Find user's review if logged in
            if (userId) {
                const existingUserReview = res.data.find(review => {
                    console.log(`Matching review ${review.id}:`);
                    console.log(`  review.user (${typeof review.user}): ${review.user}`);
                    console.log(`  userId (${typeof userId}): ${userId}`);
                    console.log(`  review.user_name: "${review.user_name}"`);
                    console.log(`  username: "${username}"`);
                    
                    const userIdMatch = review.user === userId;
                    const usernameMatch = review.user_name === username;
                    
                    console.log(`  User ID match: ${userIdMatch}`);
                    console.log(`  Username match: ${usernameMatch}`);
                    console.log(`  Overall match: ${userIdMatch || usernameMatch}`);
                    
                    // Match by user ID (most reliable) and fallback to username
                    return userIdMatch || usernameMatch;
                });
                
                console.log('=== FINAL RESULT ===');
                console.log('Found user review:', existingUserReview);
                setUserReview(existingUserReview || null);
            } else {
                console.log('No user ID provided - not logged in');
                setUserReview(null);
            }
        })
        .catch(err => {
            console.error('Failed to fetch reviews:', err);
            // Fallback: get all reviews and filter
            api.get('reviews/').then(res => {
                const bookReviews = res.data.filter(r => r.book === parseInt(id));
                console.log('Fallback: filtered reviews:', bookReviews);
                setReviews(bookReviews);
                
                // Find user's review in fallback data
                if (userId) {
                    const existingUserReview = bookReviews.find(review => 
                        review.user === userId || review.user_name === username
                    );
                    setUserReview(existingUserReview || null);
                } else {
                    setUserReview(null);
                }
            });
        });
    };

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
            if (isEditing && userReview) {
                // Update existing review
                await api.put(`reviews/${userReview.id}/`, { 
                    book: parseInt(id), 
                    content: comment, 
                    rating 
                });
                setSuccess('Review updated successfully!');
            } else {
                // Create new review
                await api.post('reviews/', { book: parseInt(id), content: comment, rating });
                setSuccess('Review submitted!');
            }
            
            setComment(''); 
            setRating(0); 
            setHoverRating(0);
            setIsEditing(false);
            
            // Refresh reviews and user review status
            loadReviews(currentUserId, currentUsername);
        } catch (err) {
            console.error('Review submission error:', err);
            if (err.response?.status === 400) {
                setError('You have already reviewed this book. You can only submit one review per book.');
            } else {
                setError('Could not submit review. Please try again.');
            }
        }
    };

    const handleEditClick = (review) => {
        setComment(review.content);
        setRating(review.rating);
        setHoverRating(0);
        setIsEditing(true);
        setError('');
        setSuccess('');
    };

    const handleCancelEdit = () => {
        setIsEditing(false);
        setComment('');
        setRating(0);
        setHoverRating(0);
        setError('');
        setSuccess('');
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
                                <div className="d-flex align-items-center gap-2">
                                    {currentUserId && (r.user === currentUserId || r.user_name === currentUsername) && (
                                        <button 
                                            className="btn btn-outline-primary btn-sm"
                                            onClick={() => handleEditClick(r)}
                                            disabled={isEditing}
                                        >
                                            <i className="bi bi-pencil"></i> Edit
                                        </button>
                                    )}
                                    <small className="text-muted">
                                        {new Date(r.created_at).toLocaleDateString()}
                                    </small>
                                </div>
                            </div>
                            <p className="mt-2 mb-0">{r.content}</p>
                        </div>
                    </div>
                ))}
            </div>
            <h5>{userReview && isEditing ? 'Edit Your Review' : userReview ? 'Add a Review' : 'Add a Review'}</h5>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            
            {!userReview || isEditing ? (
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
                    <div className="d-flex gap-2">
                        <button type="submit" className="btn btn-primary">
                            {isEditing ? 'Update Review' : 'Submit Review'}
                        </button>
                        {isEditing && (
                            <button 
                                type="button" 
                                className="btn btn-secondary"
                                onClick={handleCancelEdit}
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                </form>
            ) : (
                <div className="alert alert-info">
                    <i className="bi bi-check-circle"></i> You have already reviewed this book. 
                    Click the "Edit" button next to your review to make changes.
                </div>
            )}
        </div>
    );
}

export default BookDetailsPage; 