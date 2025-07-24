import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function AdminManageBooks() {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [editId, setEditId] = useState(null);
    const [editData, setEditData] = useState({});
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        fetchBooks();
        fetchCategories();
    }, []);

    const fetchBooks = async () => {
        const res = await api.get("/admin/books/");
        setBooks(res.data);
    };

    const fetchCategories = async () => {
        const res = await api.get("/categories/");
        setCategories(res.data);
    };

    const handleEditClick = (book) => {
        setEditId(book.id);
        setEditData({
            ...book,
            cover_image: book.cover_image, // Keep existing image reference
            available_copies: book.available_copies,
            total_copies: book.total_copies,
            category: book.category, // may be id or object, adjust as needed
        });
        setError("");
        setSuccess("");
    };

    const handleCancel = () => {
        setEditId(null);
        setEditData({});
        setError("");
        setSuccess("");
    };

    const handleChange = (e) => {
        const { name, value, files } = e.target;
        if (name === "cover_image") {
            // If a file is selected, use it; otherwise keep the current state
            if (files && files[0]) {
                setEditData((d) => ({ ...d, cover_image: files[0], newImageSelected: true }));
            }
        } else {
            setEditData((d) => ({ ...d, [name]: value }));
        }
    };

    const handleUpdate = async (book) => {
        setError("");
        setSuccess("");
        const borrowed = book.borrowed_count;
        const total = parseInt(editData.total_copies, 10);
        const available = parseInt(editData.available_copies, 10);

        if (available < 0 || total < 0) {
            setError("Copies cannot be negative.");
            return;
        }
        if (available + borrowed > total) {
            setError("Available + borrowed cannot exceed total copies.");
            return;
        }

        const formData = new FormData();
        formData.append("title", editData.title);
        formData.append("author", editData.author);
        formData.append("category", editData.category); 
        formData.append("total_copies", total);
        formData.append("available_copies", available);
        
        // Only append cover_image if a new file was selected
        if (editData.newImageSelected && editData.cover_image instanceof File) {
            formData.append("cover_image", editData.cover_image);
        }

        try {
            await api.put(`/admin/books/${book.id}/`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setSuccess("Book updated!");
            setEditId(null);
            fetchBooks();
        } catch (err) {
            setError(
                err.response?.data?.error ||
                "Update failed. Try Again."
            );
        }
    };

    const handleDelete = async (bookId) => {
        if (!window.confirm("Are you sure you want to delete this book?")) return;
        setError("");
        setSuccess("");
        try {
            await api.delete(`/admin/books/${bookId}/`);
            setSuccess("Book deleted.");
            fetchBooks();
        } catch (err) {
            setError(
                err.response?.data?.error ||
                "Delete failed. Book may have active borrowings."
            );
        }
    };

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flexShrink: 0, marginBottom: '1rem' }}>
                <h2>Manage Books</h2>
                <Link to="/admin/books/add" className="btn btn-success mb-3">
                    + Add New Book
                </Link>
                {error && <div className="alert alert-danger">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
            </div>
            <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
                <table className="table table-striped table-bordered">
                    <thead className="thead-dark" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
                        <tr>
                            <th style={{ width: '80px' }}>Cover</th>
                            <th style={{ width: '25%', maxWidth: '200px' }}>Title</th>
                            <th style={{ width: '20%' }}>Author</th>
                            <th style={{ width: '15%' }}>Category</th>
                            <th style={{ width: '8%' }}>Total</th>
                            <th style={{ width: '8%' }}>Available</th>
                            <th style={{ width: '140px' }}>Actions</th>
                        </tr>
                    </thead>
                <tbody>
                    {books.map((book) =>
                        editId === book.id ? (
                            <tr key={book.id}>
                                <td>
                                    {book.cover_image && (
                                        <img
                                            src={book.cover_image}
                                            alt="cover"
                                            style={{ width: 50, height: 70, objectFit: "cover" }}
                                        />
                                    )}
                                    <br />
                                    <input
                                        type="file"
                                        name="cover_image"
                                        accept="image/*"
                                        onChange={handleChange}
                                    />
                                    {editData.newImageSelected && (
                                        <small className="text-success">
                                            <br />New file selected: {editData.cover_image?.name}
                                        </small>
                                    )}
                                </td>
                                <td style={{ maxWidth: '200px', wordWrap: 'break-word', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                    <input
                                        type="text"
                                        name="title"
                                        value={editData.title}
                                        onChange={handleChange}
                                        className="form-control"
                                        style={{ fontSize: '14px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="author"
                                        value={editData.author}
                                        onChange={handleChange}
                                        className="form-control"
                                        style={{ fontSize: '14px' }}
                                    />
                                </td>
                                <td>
                                    <select
                                        name="category"
                                        value={editData.category}
                                        onChange={handleChange}
                                        className="form-control"
                                        style={{ fontSize: '14px' }}
                                    >
                                        {categories.map((cat) => (
                                            <option key={cat.id} value={cat.id}>
                                                {cat.name}
                                            </option>
                                        ))}
                                    </select>
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        name="total_copies"
                                        value={editData.total_copies}
                                        onChange={handleChange}
                                        className="form-control"
                                        style={{ fontSize: '14px', width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        name="available_copies"
                                        value={editData.available_copies}
                                        onChange={handleChange}
                                        className="form-control"
                                        style={{ fontSize: '14px', width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <div className="btn-group" role="group">
                                        <button
                                            className="btn btn-success btn-sm"
                                            onClick={() => handleUpdate(book)}
                                            style={{ fontSize: '12px', padding: '4px 8px' }}
                                        >
                                            Update
                                        </button>
                                        <button
                                            className="btn btn-secondary btn-sm"
                                            onClick={handleCancel}
                                            style={{ fontSize: '12px', padding: '4px 8px' }}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            <tr key={book.id}>
                                <td>
                                    {book.cover_image && (
                                        <img
                                            src={book.cover_image}
                                            alt="cover"
                                            style={{ width: 50, height: 70, objectFit: "cover" }}
                                        />
                                    )}
                                </td>
                                <td style={{ maxWidth: '200px', wordWrap: 'break-word', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    <span title={book.title}>{book.title}</span>
                                </td>
                                <td>{book.author}</td>
                                <td>
                                    {
                                        categories.find((cat) => cat.id === book.category)
                                            ?.name || book.category
                                    }
                                </td>
                                <td>{book.total_copies}</td>
                                <td>{book.available_copies}</td>
                                <td>
                                    <div className="btn-group" role="group">
                                        <button
                                            className="btn btn-primary btn-sm"
                                            onClick={() => handleEditClick(book)}
                                            style={{ fontSize: '12px', padding: '4px 8px' }}
                                        >
                                            Edit
                                        </button>
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDelete(book.id)}
                                            style={{ fontSize: '12px', padding: '4px 8px' }}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        )
                    )}
                </tbody>
            </table>
            </div>
        </div>
    );
}