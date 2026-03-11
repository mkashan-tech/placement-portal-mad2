// ===============================
// LOGIN COMPONENTS - 
// ===============================

// Student Login
const StudentLogin = {
    template: `
    <div class="card p-4">
        <h4 class="text-center">Student Login</h4>
        <div class="mb-3">
            <input v-model="email" class="form-control" placeholder="Email" type="email">
        </div>
        <div class="mb-3">
            <input v-model="password" class="form-control" placeholder="Password" type="password">
        </div>
        <button class="btn btn-primary" @click="login">Login</button>
    </div>
    `,
    data() {
        return { email: '', password: '' };
    },
    methods: {
        login() {
            window.vueApp._instance.proxy.handleLogin({
                email: this.email,
                password: this.password
            });
        }
    }
};

// Company Login
const CompanyLogin = {
    template: `
    <div class="card p-4">
        <h4 class="text-center">Company Login</h4>
        <div class="mb-3">
            <input v-model="email" class="form-control" placeholder="Email" type="email">
        </div>
        <div class="mb-3">
            <input v-model="password" class="form-control" placeholder="Password" type="password">
        </div>
        <button class="btn btn-success" @click="login">Login</button>
    </div>
    `,
    data() {
        return { email: '', password: '' };
    },
    methods: {
        login() {
            window.vueApp._instance.proxy.handleLogin({
                email: this.email,
                password: this.password
            });
        }
    }
};

// Admin Login
const AdminLogin = {
    template: `
    <div class="card p-4">
        <h4 class="text-center">Admin Login</h4>
        <div class="mb-3">
            <input v-model="email" class="form-control" placeholder="Email" type="email">
        </div>
        <div class="mb-3">
            <input v-model="password" class="form-control" placeholder="Password" type="password">
        </div>
        <button class="btn btn-warning" @click="login">Login</button>
    </div>
    `,
    data() {
        return { email: '', password: '' };
    },
    methods: {
        login() {
            window.vueApp._instance.proxy.handleLogin({
                email: this.email,
                password: this.password
            });
        }
    }
};

// Student Register
const StudentRegister = {
    template: `
    <div class="card p-4">
        <h4 class="text-center">Student Registration</h4>
        <div class="mb-3">
            <input v-model="name" class="form-control" placeholder="Full Name" required>
        </div>
        <div class="mb-3">
            <select v-model="branch" class="form-select" required>
                <option value="">Select Branch</option>
                <option>CSE</option><option>ECE</option><option>ME</option><option>DS</option>
            </select>
        <div class="mb-3">
            <input v-model="email" class="form-control" placeholder="Email" type="email">
        </div>
        <div class="mb-3">
            <input v-model="password" class="form-control" placeholder="Password" type="password">
        </div>
        <button class="btn btn-primary" @click="register">Register</button>
    </div>
    `,
    data() {
        return {name: '', branch: '', email: '', password: '',  };
    },
    methods: {
        async register() {
            try {
                const res = await axios.post('/api/register/student', {
                    name: this.name,
                    branch: this.branch,
                    email: this.email,
                    password: this.password
                });
                alert('Registration successful! Redirecting to login...');
                window.vueApp._instance.proxy.currentPage = 'studentLogin';
            } catch (err) {
                alert('Registration failed');
            }
        }
    }
};

// Company Register
const CompanyRegister = {
    template: `
    <div class="card p-4">
        <h4 class="text-center">Company Registration</h4>
        <div class="mb-3">
            <input v-model="company_name" class="form-control" placeholder="Company Name">
        </div>
        <div class="mb-3">
            <input v-model="email" class="form-control" placeholder="Email" type="email">
        </div>
        <div class="mb-3">
            <input v-model="password" class="form-control" placeholder="Password" type="password">
        </div>
        <div class="mb-3">
            <input v-model="hr_contact" class="form-control" placeholder="HR Contact (10 digits)">
        </div>
        <div class="mb-3">
            <input v-model="website" class="form-control" placeholder="Website">
        </div>
        <button class="btn btn-success" @click="register">Register</button>
    </div>
    `,
    data() {
        return {
            company_name: '',
            email: '',
            password: '',
            hr_contact: '',
            website: ''
        };
    },
    methods: {
        async register() {
            try {
                const res = await axios.post('/api/register/company', {
                    company_name: this.company_name,
                    email: this.email,
                    password: this.password,
                    hr_contact: this.hr_contact,
                    website: this.website
                });
                alert(res.data.message);
                window.vueApp._instance.proxy.currentPage = 'home';
            } catch (err) {
                alert('Registration failed');
            }
        }
    }
};

// Mount all components
window.addEventListener('DOMContentLoaded', () => {
    const mounts = {
        '#student-login-component': StudentLogin,
        '#company-login-component': CompanyLogin,
        '#admin-login-component': AdminLogin,
        '#student-register-component': StudentRegister,
        '#company-register-component': CompanyRegister
    };
    
    for (const [sel, comp] of Object.entries(mounts)) {
        const el = document.querySelector(sel);
        if (el) {
            const app = Vue.createApp(comp);
            // Ensure child apps also respect the same delimiter if they display data
            app.config.compilerOptions.delimiters = ['[[', ']]'];
            app.mount(sel);
        }
    }
});