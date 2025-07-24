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
        
        // Client-side validation: Check if category already exists
        const categoryExists = categories.some(cat => 
            cat.name.toLowerCase().trim() === newCategory.toLowerCase().trim()
        );
        
        if (categoryExists) {
            setError(`Category "${newCategory}" already exists. Please choose a different name.`);
            return;
        }
        
        try {
            await api.post('admin/categories/', { name: newCategory.trim() });
            setSuccess('Category added successfully.');
            setNewCategory('');
            fetchCategories();
        } catch (err) {
            console.error('Add category error:', err);
            if (err.response?.status === 400) {
                // Handle backend validation errors
                const errorData = err.response.data;
                if (errorData.name && errorData.name.includes('already exists')) {
                    setError(`Category "${newCategory}" already exists. Please choose a different name.`);
                } else if (errorData.name) {
                    setError(`Error: ${errorData.name[0]}`);
                } else {
                    setError('Invalid category data. Please check your input.');
                }
            } else {
                setError('Could not add category. Please try again.');
            }
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
        
        // Client-side validation: Check if category name already exists (excluding current category)
        const categoryExists = categories.some(cat => 
            cat.id !== id && cat.name.toLowerCase().trim() === editName.toLowerCase().trim()
        );
        
        if (categoryExists) {
            setError(`Category "${editName}" already exists. Please choose a different name.`);
            return;
        }
        
        try {
            await api.put(`admin/categories/${id}/`, { name: editName.trim() });
            setSuccess('Category updated successfully.');
            setEditId(null);
            setEditName('');
            fetchCategories();
        } catch (err) {
            console.error('Update category error:', err);
            if (err.response?.status === 400) {
                // Handle backend validation errors
                const errorData = err.response.data;
                if (errorData.name && errorData.name.includes('already exists')) {
                    setError(`Category "${editName}" already exists. Please choose a different name.`);
                } else if (errorData.name) {
                    setError(`Error: ${errorData.name[0]}`);
                } else {
                    setError('Invalid category data. Please check your input.');
                }
            } else {
                setError('Could not update category. Please try again.');
            }
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
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flexShrink: 0, marginBottom: '1rem' }}>
                <h2>Manage Categories</h2>
                {error && <div className="alert alert-danger">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
                <form className="mb-4 d-flex" onSubmit={handleAdd}>
                    <input type="text" className="form-control me-2" placeholder="New category name" value={newCategory} onChange={e => setNewCategory(e.target.value)} required />
                    <button className="btn btn-success" type="submit">Add</button>
                </form>
            </div>
            <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
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
                            <thead style={{ position: 'sticky', top: 0, zIndex: 10, backgroundColor: '#f8f9fa' }}>
                                <tr>
                                    <th style={{ width: '70%' }}>Name</th>
                                    <th style={{ width: '30%' }}>Actions</th>
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
                                            <div className="btn-group" role="group">
                                                <button className="btn btn-primary btn-sm" onClick={() => handleUpdate(cat.id)} style={{ fontSize: '12px', padding: '4px 8px' }}>Save</button>
                                                <button className="btn btn-secondary btn-sm" onClick={() => setEditId(null)} style={{ fontSize: '12px', padding: '4px 8px' }}>Cancel</button>
                                            </div>
                                        ) : (
                                            <div className="btn-group" role="group">
                                                <button className="btn btn-warning btn-sm" onClick={() => handleEdit(cat.id, cat.name)} style={{ fontSize: '12px', padding: '4px 8px' }}>Edit</button>
                                                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(cat.id)} style={{ fontSize: '12px', padding: '4px 8px' }}>Delete</button>
                                            </div>
                                        )}
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

export default AdminManageCategoriesPage; 