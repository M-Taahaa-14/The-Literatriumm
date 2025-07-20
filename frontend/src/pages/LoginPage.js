import React, { useState } from 'react';
import api from '../api';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const res = await api.post('login/', { username, password });
            if (res.data.token) {
                localStorage.setItem('token', res.data.token);
                localStorage.setItem('is_admin', res.data.is_admin);
                localStorage.setItem('full_name', res.data.full_name);
                window.location.href = res.data.is_admin ? '/admin/dashboard' : '/';
            } else {
                setError('Invalid response from server.');
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed.');
        }
    };

    return (
        <div className="row justify-content-center align-items-center min-vh-100" style={{ minHeight: '100vh' }}>
            <div className="col-md-6 mt-5 mt-md-0">
                <h2>Login</h2>
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleLogin} className="card p-4">
                    <div className="mb-3">
                        <label className="form-label">Username</label>
                        <input type="text" className="form-control" value={username} onChange={e => setUsername(e.target.value)} required />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Password</label>
                        <input type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">Login</button>
                    <a href="/signup" className="d-block text-center mt-3">Don't have an account? Sign up</a>
                </form>
            </div>
        </div>
    );
}

export default LoginPage; 