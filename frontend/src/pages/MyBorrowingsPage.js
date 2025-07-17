import React, { useEffect, useState } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function MyBorrowingsPage() {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [actionMessage, setActionMessage] = useState('');

    const fetchRecords = () => {
        api.get('user_borrowings/')
            .then(res => {
                setRecords(res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Could not fetch borrowings.');
                setLoading(false);
            });
    };

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in to view your borrowings.');
            setLoading(false);
            return;
        }
        fetchRecords();
    }, []);

    const handleReturn = (recordId) => {
        setActionMessage('');
        api.post(`return/${recordId}/`)
            .then(res => {
                setActionMessage(res.data.message || 'Book returned successfully.');
                fetchRecords();
            })
            .catch(err => {
                setActionMessage('Failed to return book.');
            });
    };

    return (
        <div>
            <h2>My Borrowings</h2>
            {actionMessage && <div className="alert alert-info">{actionMessage}</div>}
            {loading ? (
                <div className="text-center my-5">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            ) : error ? (
                <div className="alert alert-danger">{error}</div>
            ) : records.length === 0 ? (
                <p>You have not borrowed any books yet.</p>
            ) : (
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Book</th>
                                <th>Borrow Date</th>
                                <th>Due Date</th>
                                <th>Return Date</th>
                                <th>Fine</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records.map(record => (
                                <tr key={record.id}>
                                    <td><Link to={`/books/${record.book}`}>{record.book_title}</Link></td>
                                    <td>{record.borrow_date ? new Date(record.borrow_date).toLocaleDateString() : ''}</td>
                                    <td>{record.due_date ? new Date(record.due_date).toLocaleDateString() : ''}</td>
                                    <td>{record.return_date ? new Date(record.return_date).toLocaleDateString() : 'Not returned'}</td>
                                    <td>{record.fine ? `$${record.fine}` : '-'}</td>
                                    <td>
                                    <button
                                        className={`btn btn-sm ${record.return_date ? 'btn-secondary' : 'btn-success'}`}
                                        onClick={() => !record.return_date && handleReturn(record.id)}
                                        disabled={!!record.return_date}
                                    >
                                        {record.return_date ? 'Returned' : 'Return'}
                                    </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default MyBorrowingsPage;
