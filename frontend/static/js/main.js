// ==========================================
// MAIN VUE APP - 
// ========================================

const vueApp = Vue.createApp({
    data() {
        return {
            currentPage: 'home',
            user: null
        };
    },

    methods: {
        async checkSession() {
            try {
                const res = await axios.get('/api/me');
                if (res.data.logged_in) {
                    this.user = { role: res.data.role };
                    
                    // Dashboard par sirf tabhi bhejein jab user home page par ho
                    // Isse baar-baar alert aane wala issue solve ho jayega
                    if (this.currentPage === 'home') {
                        this.currentPage = res.data.role + 'Dashboard';
                    }
                } else {
                    // Agar login nahi hai toh silent rahein, koi alert na dikhayein
                    this.user = null;
                }
            } catch (err) {
                // Session check background mein fail hone par console mein log karein, 
                // user ko disturb na karein.
                console.log('Session check: Not logged in.');
            }
        },

        async handleLogin(credentials) {
            try {
                const res = await axios.post('/api/login', credentials);
                
                // Success message hata diya gaya hai (Automatic redirection)
                this.user = { role: res.data.role };
                
                if (res.data.role === 'admin') this.currentPage = 'adminDashboard';
                else if (res.data.role === 'company') this.currentPage = 'companyDashboard';
                else if (res.data.role === 'student') this.currentPage = 'studentDashboard';
                
            } catch (err) {
                // Security check fail hone par (Wrong password/Deactivated) user ko batana zaroori hai
                alert(err.response?.data?.message || 'Login failed. Please check credentials.');
            }
        },

        async logout() {
            try {
                await axios.get('/api/me'); // Just to verify current status if needed
                await axios.get('/api/logout');
                
                this.user = null;
                this.currentPage = 'home';
                
                // alert('You have been logged out.'); <--- Is line ko delete ya comment kar diya hai
                console.log("Logged out successfully"); // Yeh console mein dikhega, screen par nahi
            } catch (err) {
                // Sirf galti hone par hi user ko disturb karein
                console.error("Logout error", err);
                this.user = null;
                this.currentPage = 'home';
            }
        }
    },

    mounted() {
        // Axios settings
        axios.defaults.baseURL = 'http://127.0.0.1:5000';
        axios.defaults.withCredentials = true;
        
        // Initial session check
        this.checkSession();
    }
});

// Register components
vueApp.component('admin-dashboard', AdminDashboard);
vueApp.component('company-dashboard', CompanyDashboard);
vueApp.component('student-dashboard', StudentDashboard);

// Fix delimiters -
vueApp.config.compilerOptions.delimiters = ['[[', ']]'];

// Mount
window.vueApp = vueApp;
vueApp.mount('#app');