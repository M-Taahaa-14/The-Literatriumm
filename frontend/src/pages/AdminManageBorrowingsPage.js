import React, { useEffect, useState } from 'react';
import api from '../api';

function AdminManageBorrowingsPage() {
    const [borrowings, setBorrowings] = useState([]);
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [fineAmount, setFineAmount] = useState({});

    const fetchBorrowings = () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in as admin to manage borrowings.');
            setLoading(false);
            return;
        }
        setLoading(true);
        api.get('admin/borrowings/', {
            params: status ? { status } : {}
        })
            .then(res => {
                setBorrowings(res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Could not fetch borrowings.');
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchBorrowings();
        // eslint-disable-next-line
    }, [status]);

    const handleAction = async (action, borrowId) => {
        const token = localStorage.getItem('token');
        if (!token) return;
        setError(''); setSuccess('');
        let data = { action, borrow_id: borrowId };
        if (action === 'fine') {
            data.fine_amount = fineAmount[borrowId] || 0;
        }
        try {
            await api.post('admin/borrowings/action/', data);
            setSuccess(`Action '${action}' successful.`);
            fetchBorrowings();
        } catch {
            setError(`Could not perform action '${action}'.`);
        }
    };

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flexShrink: 0, marginBottom: '1rem' }}>
                <h2>Manage Borrowings</h2>
                <div className="row mb-4">
                    <div className="col-md-6">
                        <div className="d-flex align-items-center">
                            <label className="form-label me-2 mb-0">Filter by status:</label>
                            <select 
                                className="form-select" 
                                value={status} 
                                onChange={e => setStatus(e.target.value)}
                                style={{ width: 'auto' }}
                            >
                                <option value="">All Borrowings</option>
                                <option value="returned">✅ Returned</option>
                                <option value="unreturned">⏳ Unreturned</option>
                                <option value="overdue">⚠️ Overdue</option>
                            </select>
                        </div>
                    </div>
                    <div className="col-md-6 text-end">
                        <button 
                            className="btn btn-outline-secondary btn-sm"
                            onClick={fetchBorrowings}
                            title="Refresh data"
                        >
                            <i className="fas fa-sync-alt me-1"></i>
                            Refresh
                        </button>
                    </div>
                </div>
                {!loading && borrowings.length > 0 && (
                    <div className="row mb-3">
                        <div className="col-12">
                            <div className="card bg-light">
                                <div className="card-body">
                                    <div className="row text-center">
                                        <div className="col-md-3">
                                            <h6 className="text-muted">Total Borrowings</h6>
                                            <h5 className="mb-0">{borrowings.length}</h5>
                                        </div>
                                        <div className="col-md-3">
                                            <h6 className="text-muted">Returned</h6>
                                            <h5 className="mb-0 text-success">{borrowings.filter(b => b.is_returned).length}</h5>
                                        </div>
                                        <div className="col-md-3">
                                            <h6 className="text-muted">Unreturned</h6>
                                            <h5 className="mb-0 text-warning">{borrowings.filter(b => !b.is_returned).length}</h5>
                                        </div>
                                        <div className="col-md-3">
                                            <h6 className="text-muted">Overdue</h6>
                                            <h5 className="mb-0 text-danger">
                                                {borrowings.filter(b => !b.is_returned && b.due_date && new Date() > new Date(b.due_date)).length}
                                            </h5>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                {error && <div className="alert alert-danger">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
            </div>
            <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
                {loading ? (
                    <div className="text-center my-5">
                        <div className="spinner-border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                ) : borrowings.length === 0 ? (
                    <p>No borrowings found.</p>
                ) : (
                    <div className="table-responsive">
                        <table className="table table-striped">
                            <thead style={{ position: 'sticky', top: 0, zIndex: 10, backgroundColor: '#f8f9fa' }}>
                                <tr>
                                    <th style={{ width: '14%' }}>User</th>
                                    <th style={{ width: '16%' }}>Book</th>
                                    <th style={{ width: '10%' }}>Borrow Date</th>
                                    <th style={{ width: '10%' }}>Due Date</th>
                                    <th style={{ width: '10%' }}>Return Date</th>
                                    <th style={{ width: '8%' }}>Fine</th>
                                    <th style={{ width: '12%' }}>Status</th>
                                    <th style={{ width: '20%' }}>Actions</th>
                                </tr>
                            </thead>
                        <tbody>
                            {borrowings.map(borrow => (
                                <tr key={borrow.id}>
                                    <td>{borrow.username}</td>
                                    <td>{borrow.book_title}</td>
                                    <td>{borrow.borrow_date ? new Date(borrow.borrow_date).toLocaleDateString() : ''}</td>
                                    <td>{borrow.due_date ? new Date(borrow.due_date).toLocaleDateString() : ''}</td>
                                    <td>{borrow.return_date ? new Date(borrow.return_date).toLocaleDateString() : 'Not returned'}</td>
                                    <td>{borrow.fine ? `$${borrow.fine}` : '-'}</td>
                                    <td>
                                        {borrow.is_returned ? (
                                            <span className="badge bg-success">Returned</span>
                                        ) : borrow.due_date && new Date() > new Date(borrow.due_date) ? (
                                            <span className="badge bg-danger">Overdue</span>
                                        ) : (
                                            <span className="badge bg-warning text-dark">Unreturned</span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="d-flex align-items-center gap-1" style={{ flexWrap: 'nowrap', minWidth: '200px' }}>
                                            <button
                                                className="btn btn-outline-primary btn-sm"
                                                onClick={() => handleAction('reminder', borrow.id)}
                                                disabled={borrow.is_returned}
                                                title="Send reminder to user"
                                                style={{ fontSize: '12px', padding: '6px 10px', whiteSpace: 'nowrap', flexShrink: 0, minWidth: '70px' }}
                                            >
                                                <i className="fas fa-bell me-1"></i>
                                                Reminder
                                            </button>
                                            
                                            <input
                                                type="number"
                                                className="form-control form-control-sm"
                                                placeholder="Fine"
                                                value={fineAmount[borrow.id] || ''}
                                                onChange={e => setFineAmount({ ...fineAmount, [borrow.id]: e.target.value })}
                                                min="0"
                                                step="0.01"
                                                style={{ width: '70px', fontSize: '12px', flexShrink: 0 }}
                                                disabled={borrow.is_returned}
                                            />
                                            
                                            <button
                                                className="btn btn-outline-warning btn-sm"
                                                onClick={() => handleAction('fine', borrow.id)}
                                                disabled={borrow.is_returned || !fineAmount[borrow.id]}
                                                title="Update fine amount"
                                                style={{ fontSize: '12px', padding: '6px 10px', whiteSpace: 'nowrap', flexShrink: 0, minWidth: '60px' }}
                                            >
                                                <i className="fas fa-dollar-sign me-1"></i>
                                                Fine
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                )}
            </div>
        </div>
    );
}

export default AdminManageBorrowingsPage;