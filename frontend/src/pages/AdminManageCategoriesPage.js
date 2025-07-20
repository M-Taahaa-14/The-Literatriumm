import React, { useEffect, useState } from 'react';
import api from '../api';

function AdminManageCategoriesPage() {
    const [categories, setCategories] = useState([]);
    const [newCategory, setNewCategory] = useState('');
    const [editId, setEditId] = useState(null);
    const [editName, setEditName] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(true);

    const fetchCategories = () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in as admin to manage categories.');
            setLoading(false);
            return;
        }
        setLoading(true);
        api.get('admin/categories/')
            .then(res => {
                setCategories(res.data.results || res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Could not fetch categories.');
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchCategories();
        // eslint-disable-next-line
    }, []);

    const handleAdd = async (e) => {
        e.preventDefault();
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            await api.post('admin/categories/', { name: newCategory });
            setSuccess('Category added.');
            setNewCategory('');
            fetchCategories();
        } catch {
            setError('Could not add category.');
        }
    };

    const handleEdit = (id, name) => {
        setEditId(id);
        setEditName(name);
    };

    const handleUpdate = async (id) => {
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            await api.put(`admin/categories/${id}/`, { name: editName });
            setSuccess('Category updated.');
            setEditId(null);
            setEditName('');
            fetchCategories();
        } catch {
            setError('Could not update category.');
        }
    };

    const handleDelete = async (id) => {
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            await api.delete(`admin/categories/${id}/`);
            setSuccess('Category deleted.');
            fetchCategories();
        } catch {
            setError('Could not delete category.');
        }
    };

    return (
        <div>
            <h2>Manage Categories</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form className="mb-4 d-flex" onSubmit={handleAdd}>
                <input type="text" className="form-control me-2" placeholder="New category name" value={newCategory} onChange={e => setNewCategory(e.target.value)} required />
                <button className="btn btn-success" type="submit">Add</button>
            </form>
            {loading ? (
                <div className="text-center my-5">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            ) : categories.length === 0 ? (
                <p>No categories found.</p>
            ) : (
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {categories.map(cat => (
                                <tr key={cat.id}>
                                    <td>
                                        {editId === cat.id ? (
                                            <input type="text" className="form-control" value={editName} onChange={e => setEditName(e.target.value)} />
                                        ) : (
                                            cat.name
                                        )}
                                    </td>
                                    <td>
                                        {editId === cat.id ? (
                                            <>
                                                <button className="btn btn-primary btn-sm me-2" onClick={() => handleUpdate(cat.id)}>Save</button>
                                                <button className="btn btn-secondary btn-sm" onClick={() => setEditId(null)}>Cancel</button>
                                            </>
                                        ) : (
                                            <>
                                                <button className="btn btn-warning btn-sm me-2" onClick={() => handleEdit(cat.id, cat.name)}>Edit</button>
                                                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(cat.id)}>Delete</button>
                                            </>
                                        )}
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

export default AdminManageCategoriesPage; 