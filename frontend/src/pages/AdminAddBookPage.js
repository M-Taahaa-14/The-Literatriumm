import React, { useEffect, useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

function AdminAddBookPage() {
    const [form, setForm] = useState({
        title: '',
        author: '',
        category: '',
        total_copies: '',
        available_copies: '',
        cover_image: null
    });
    const [categories, setCategories] = useState([]);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        api.get('categories/')
            .then(res => setCategories(res.data))
            .catch(() => setCategories([]));
    }, []);

    const handleChange = e => {
        const { name, value, files } = e.target;
        if (name === 'cover_image') {
            setForm({ ...form, cover_image: files[0] });
        } else {
            setForm({ ...form, [name]: value });
        }
    };

    const handleSubmit = async e => {
        e.preventDefault();
        setError(''); setSuccess(''); setLoading(true);
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in as admin to add books.');
            setLoading(false);
            return;
        }
        const data = new FormData();
        Object.entries(form).forEach(([k, v]) => v && data.append(k, v));
        try {
            await api.post('admin/books/', data);
            setSuccess('Book added successfully!');
            setForm({ title: '', author: '', category: '', total_copies: '', available_copies: '', cover_image: null });
            setTimeout(() => navigate('/admin/books'), 1200);
        } catch {
            setError('Could not add book.');
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Add Book</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form className="card p-4" onSubmit={handleSubmit} encType="multipart/form-data">
                <div className="mb-3">
                    <label className="form-label">Title</label>
                    <input type="text" className="form-control" name="title" value={form.title} onChange={handleChange} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Author</label>
                    <input type="text" className="form-control" name="author" value={form.author} onChange={handleChange} required />
                </div>
                <div className="mb-3">
                    <label className="form-label">Category</label>
                    <select className="form-select" name="category" value={form.category} onChange={handleChange} required>
                        <option value="">Select</option>
                        {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                    </select>
                </div>
                <div className="mb-3">
                    <label className="form-label">Total Copies</label>
                    <input type="number" className="form-control" name="total_copies" value={form.total_copies} onChange={handleChange} required min="1" />
                </div>
                <div className="mb-3">
                    <label className="form-label">Available Copies</label>
                    <input type="number" className="form-control" name="available_copies" value={form.available_copies} onChange={handleChange} required min="0" />
                </div>
                <div className="mb-3">
                    <label className="form-label">Cover Image</label>
                    <input type="file" className="form-control" name="cover_image" accept="image/*" onChange={handleChange} />
                </div>
                <button type="submit" className="btn btn-success" disabled={loading}>{loading ? 'Adding...' : 'Add Book'}</button>
            </form>
        </div>
    );
}

export default AdminAddBookPage; 