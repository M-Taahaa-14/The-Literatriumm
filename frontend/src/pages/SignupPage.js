import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

function SignupPage() {
    const [form, setForm] = useState({ username: '', password: '', full_name: '', address: '', phone: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = e => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await api.post('signup/', form);
            navigate('/login');
        } catch (err) {
            setError('Signup failed. Please check your details.');
        }
    };

    return (
        <div className="row justify-content-center align-items-center min-vh-100" style={{ minHeight: '100vh' }}>
            <div className="col-md-6 mt-5 mt-md-0">
                <h2>Signup</h2>
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleSubmit} className="card p-4">
                    <div className="mb-3">
                        <label className="form-label">Username</label>
                        <input type="text" className="form-control" name="username" value={form.username} onChange={handleChange} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Password</label>
                        <input type="password" className="form-control" name="password" value={form.password} onChange={handleChange} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Full Name</label>
                        <input type="text" className="form-control" name="full_name" value={form.full_name} onChange={handleChange} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Address</label>
                        <input type="text" className="form-control" name="address" value={form.address} onChange={handleChange} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Phone</label>
                        <input type="text" className="form-control" name="phone" value={form.phone} onChange={handleChange} required />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">Signup</button>
                    <a href="/login" className="d-block text-center mt-3">Already have an account? Login</a>
                </form>
            </div>
        </div>
    );
}

export default SignupPage; 