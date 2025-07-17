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
            cover_image: null, // for new upload
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
            setEditData((d) => ({ ...d, cover_image: files[0] }));
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
        if (editData.cover_image) {
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
        <div className="container mt-4">
            <h2>Manage Books</h2>
            <Link to="/admin/books/add" className="btn btn-success mb-3">
                + Add New Book
            </Link>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <table className="table table-striped table-bordered">
                <thead className="thead-dark">
                    <tr>
                        <th>Cover</th>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Category</th>
                        <th>Total</th>
                        <th>Available</th>
                        <th>Actions</th>
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
                                    <input
                                        type="file"
                                        name="cover_image"
                                        accept="image/*"
                                        onChange={handleChange}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="title"
                                        value={editData.title}
                                        onChange={handleChange}
                                        className="form-control"
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="author"
                                        value={editData.author}
                                        onChange={handleChange}
                                        className="form-control"
                                    />
                                </td>
                                <td>
                                    <select
                                        name="category"
                                        value={editData.category}
                                        onChange={handleChange}
                                        className="form-control"
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
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        name="available_copies"
                                        value={editData.available_copies}
                                        onChange={handleChange}
                                        className="form-control"
                                    />
                                </td>
                                <td>
                                    <button
                                        className="btn btn-success btn-sm mr-2"
                                        onClick={() => handleUpdate(book)}
                                    >
                                        Update
                                    </button>
                                    <button
                                        className="btn btn-secondary btn-sm"
                                        onClick={handleCancel}
                                    >
                                        Cancel
                                    </button>
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
                                <td>{book.title}</td>
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
                                    <button
                                        className="btn btn-primary btn-sm mr-2"
                                        onClick={() => handleEditClick(book)}
                                    >
                                        Edit
                                    </button>
                                    <button
                                        className="btn btn-danger btn-sm"
                                        onClick={() => handleDelete(book.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        )
                    )}
                </tbody>
            </table>
        </div>
    );
}