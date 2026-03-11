// ===============================
// ADMIN DASHBOARD - 
// ===============================

const AdminDashboard = {
    template: `
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Admin Dashboard</h2>
            <div>
                <button class="btn btn-outline-primary" :class="{active: tab==='dashboard'}" @click="tab='dashboard'">Dashboard</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='students'}" @click="tab='students'">Students</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='companies'}" @click="tab='companies'">Companies</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='drives'}" @click="tab='drives'">Drives</button>
            </div>
        </div>

        <div v-if="tab==='dashboard'" class="row">
            <div class="col-md-3 mb-3">
                <div class="card text-center p-3">
                    <h6>Total Students</h6>
                    <h3>[[ stats.total_students || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card text-center p-3">
                    <h6>Total Companies</h6>
                    <h3>[[ stats.total_companies || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card text-center p-3">
                    <h6>Total Drives</h6>
                    <h3>[[ stats.total_jobs || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card text-center p-3">
                    <h6>Total Applications</h6>
                    <h3>[[ stats.total_applications || 0 ]]</h3>
                </div>
            </div>
            <div class="mt-4 p-3 bg-light border rounded text-center">
                <h5 class="mb-3">Admin Insights</h5>
                <button class="btn btn-danger me-2" @click="generateReport">Generate New Report</button>
                <a href="http://127.0.0.1:5000/api/admin/view-report" target="_blank" class="btn btn-outline-dark">
                    View Latest Report
                </a>
            </div>
            
            <div class="col-md-6 mt-4">
                <div class="card">
                    <div class="card-header bg-warning">
                        Pending Companies ([[ pendingCompanies.length ]])
                    </div>
                    <div class="card-body">
                        <div v-for="c in pendingCompanies" :key="c.id" class="border-bottom mb-2 pb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>[[ c.company_name ]]</strong><br>
                                    <small>[[ c.email ]] | Contact: [[ c.hr_contact ]]</small>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-success me-1" @click="approveCompany(c.id)">✓</button>
                                    <button class="btn btn-sm btn-danger" @click="rejectCompany(c.id)">✗</button>
                                </div>
                            </div>
                        </div>
                        <div v-if="pendingCompanies.length===0" class="text-muted">No pending approvals</div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mt-4">
                <div class="card">
                    <div class="card-header bg-warning">
                        Pending Drives ([[ pendingDrives.length ]])
                    </div>
                    <div class="card-body">
                        <div v-for="d in pendingDrives" :key="d.id" class="border-bottom mb-2 pb-2">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <strong>[[ d.title ]]</strong> at [[ d.company ]]<br>
                                    <small>Salary: [[ d.salary ]] LPA</small>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-success me-1" @click="approveDrive(d.id)">✓</button>
                                    <button class="btn btn-sm btn-danger" @click="rejectDrive(d.id)">✗</button>
                                </div>
                            </div>
                        </div>
                        <div v-if="pendingDrives.length===0" class="text-muted">No pending drives</div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="tab==='students'">
            <h4>Manage Students</h4>
            
            <div class="row mb-3">
                <div class="col-md-4">
                    <input class="form-control" placeholder="Search by name..." v-model="studentSearch" @input="searchStudents">
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary" @click="searchStudents">Search</button>
                </div>
                <div class="col-md-2">
                    <select class="form-select" v-model="branchFilter" @change="filterStudents">
                        <option value="">All Branches</option>
                        <option>CSE</option><option>ECE</option><option>ME</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <input class="form-control" placeholder="Min CGPA" v-model="minCgpa" type="number" step="0.1" @input="filterStudents">
                </div>
            </div>

            <table class="table table-bordered table-hover">
                <thead class="table-light">
                    <tr>
                        <th>ID</th><th>Name</th><th>Branch</th><th>CGPA</th>
                        <th>Status</th><th>Profile</th><th>Applications</th><th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="s in filteredStudents" :key="s.id">
                        <td>[[ s.id ]]</td>
                        <td>[[ s.name ]]</td>
                        <td>[[ s.branch ]]</td>
                        <td>[[ s.cgpa ]]</td>
                        <td>
                            <span class="badge" :class="s.is_active ? 'bg-success' : 'bg-danger'">
                                [[ s.is_active ? 'Active' : 'Deactivated' ]]
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="viewStudentProfile(s.id)">View</button>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-warning" @click="viewStudentApps(s.id)">View ([[ s.app_count || 0 ]])</button>
                        </td>
                        <td>
                            <button class="btn btn-sm" :class="s.is_active ? 'btn-warning' : 'btn-success'"
                                    @click="toggleStudent(s)">
                                [[ s.is_active ? 'Deactivate' : 'Activate' ]]
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="tab==='companies'">
            <h4>Manage Companies</h4>
            
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>ID</th><th>Name</th><th>Contact</th>
                        <th>Approval</th><th>Status</th><th>Jobs</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="c in companies" :key="c.id">
                        <td>[[ c.id ]]</td>
                        <td>[[ c.company_name ]]</td>
                        <td>[[ c.hr_contact ]]</td>
                        <td>
                            <span class="badge" :class="c.approved ? 'bg-success' : 'bg-warning'">
                                [[ c.approved ? 'Approved' : 'Pending' ]]
                            </span>
                        </td>
                        <td>
                            <span class="badge" :class="c.is_active ? 'bg-success' : 'bg-danger'">
                                [[ c.is_active ? 'Active' : 'Blocked' ]]
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="viewCompanyJobs(c.id)">View ([[ c.jobs_count || 0 ]])</button>
                        </td>
                        <td>
                            <button v-if="!c.approved" class="btn btn-sm btn-success me-1" @click="approveCompany(c.id)">Approve</button>
                            <button class="btn btn-sm" :class="c.is_active ? 'btn-warning' : 'btn-success'"
                                    @click="toggleCompany(c)">
                                [[ c.is_active ? 'Deactivate' : 'Activate' ]]
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="tab==='drives'">
            <h4>Placement Drives</h4>
            
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>ID</th><th>Company</th><th>Title</th><th>Salary</th>
                        <th>Approval</th><th>Status</th><th>Applicants</th><th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="d in drives" :key="d.id">
                        <td>[[ d.id ]]</td>
                        <td>[[ d.company ]]</td>
                        <td>[[ d.title ]]</td>
                        <td>[[ d.salary ]] LPA</td>
                        <td>
                            <span class="badge" :class="d.approved ? 'bg-success' : 'bg-warning'">
                                [[ d.approved ? 'Approved' : 'Pending' ]]
                            </span>
                        </td>
                        <td>[[ d.status ]]</td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="viewDriveApplicants(d.id)">View ([[ d.applicants_count || 0 ]])</button>
                        </td>
                        <td>
                            <button v-if="!d.approved" class="btn btn-sm btn-success" @click="approveDrive(d.id)">Approve</button>
                            <button v-if="d.status==='Active'" class="btn btn-sm btn-warning" @click="closeDrive(d.id)">Close</button>
                            <button v-if="d.status==='Closed'" class="btn btn-sm btn-success" @click="reopenDrive(d.id)">Reopen</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="showProfileModal" class="modal fade show" style="display:block; background:rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5>Student Profile: [[ selectedStudent.name ]]</h5>
                        <button type="button" class="btn-close" @click="showProfileModal=false"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Email:</strong> [[ selectedStudent.email ]]</p>
                        <p><strong>Branch:</strong> [[ selectedStudent.branch ]]</p>
                        <p><strong>CGPA:</strong> [[ selectedStudent.cgpa ]]</p>
                        <p><strong>Skills:</strong> [[ selectedStudent.skills ]]</p>
                        <p><strong>Education:</strong> [[ selectedStudent.education ]]</p>
                        <p><strong>Experience:</strong> [[ selectedStudent.experience ]]</p>
                        <p v-if="selectedStudent.resume">
                            <strong>Resume:</strong> 
                            <a :href="selectedStudent.resume" target="_blank">Download</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `,

    data() {
        return {
            tab: 'dashboard',
            stats: {},
            students: [],
            filteredStudents: [],
            companies: [],
            drives: [],
            pendingCompanies: [],
            pendingDrives: [],
            studentSearch: '',
            branchFilter: '',
            minCgpa: '',
            showProfileModal: false,
            selectedStudent: {}
        };
    },

    methods: {
        async loadStats() {
            const res = await axios.get('/api/admin/dashboard');
            this.stats = res.data;
        },

        async loadStudents() {
            const res = await axios.get('/api/admin/students');
            this.students = res.data;
            this.filteredStudents = this.students;
        },

        async loadCompanies() {
            const res = await axios.get('/api/admin/companies');
            this.companies = res.data;
        },

        async loadDrives() {
            const res = await axios.get('/api/admin/drives');
            this.drives = res.data;
        },

        async loadPendingCompanies() {
            const res = await axios.get('/api/admin/pending-companies');
            this.pendingCompanies = res.data;
        },

        async loadPendingDrives() {
            const res = await axios.get('/api/admin/pending-jobs');
            this.pendingDrives = res.data;
        },

        filterStudents() {
            this.filteredStudents = this.students.filter(s => {
                let match = true;
                if (this.branchFilter && s.branch !== this.branchFilter) match = false;
                if (this.minCgpa && s.cgpa < parseFloat(this.minCgpa)) match = false;
                return match;
            });
        },

        async searchStudents() {
            if (this.studentSearch) {
                const res = await axios.get(`/api/admin/search-students?q=${this.studentSearch}`);
                this.filteredStudents = res.data;
            } else {
                this.filteredStudents = this.students;
            }
        },

        async viewStudentProfile(studentId) {
            const res = await axios.get(`/api/admin/student-profile/${studentId}`);
            this.selectedStudent = res.data;
            this.showProfileModal = true;
        },

        async viewStudentApps(studentId) {
            const res = await axios.get(`/api/admin/students-application/${studentId}`);
            let msg = "Applications:\n";
            res.data.forEach(app => {
                msg += `${app.job_title} - ${app.status} (${new Date(app.applied_on).toLocaleDateString()})\n`;
            });
            alert(msg);
        },

        async viewCompanyJobs(companyId) {
            const res = await axios.get(`/api/admin/company-jobs/${companyId}`);
            let msg = "Company Jobs:\n";
            res.data.forEach(job => {
                msg += `${job.title} - ${job.status} (${job.applicants_count} applicants)\n`;
            });
            alert(msg);
        },

        async viewDriveApplicants(driveId) {
            const res = await axios.get(`/api/admin/job-applicants/${driveId}`);
            let msg = "Applicants:\n";
            res.data.forEach(app => {
                msg += `${app.name} (${app.branch}, CGPA:${app.cgpa}) - ${app.status}\n`;
            });
            alert(msg);
        },

        async approveCompany(id) {
            await axios.put(`/api/admin/approve-company/${id}`);
            alert('Company approved');
            this.loadCompanies();
            this.loadPendingCompanies();
        },

        async rejectCompany(id) {
            await axios.put(`/api/admin/deactivate-company/${id}`);
            alert('Company rejected');
            this.loadCompanies();
            this.loadPendingCompanies();
        },

        async approveDrive(id) {
            await axios.put(`/api/admin/approve-job/${id}`);
            alert('Drive approved');
            this.loadDrives();
            this.loadPendingDrives();
        },

        async rejectDrive(id) {
            await axios.put(`/api/admin/reject-job/${id}`);
            alert('Drive rejected');
            this.loadDrives();
            this.loadPendingDrives();
        },

        async closeDrive(id) {
            await axios.put(`/api/admin/close-drive/${id}`);
            alert('Drive closed');
            this.loadDrives();
        },

        async reopenDrive(id) {
            await axios.put(`/api/admin/reopen-drive/${id}`);
            this.loadDrives();
        },

        async toggleStudent(s) {
            try {
                const res = await axios.put(`/api/admin/toggle-student/${s.id}`);
                
                console.log("New Status from Server:", res.data.current_status);

                alert(res.data.message);

                await this.loadStudents(); 
                
            } catch (err) {
                console.error("Toggle error:", err);
                alert("Action failed: " + (err.response?.data?.message || "Server error"));
            }
        },

        async toggleCompany(c) {
            await axios.put(`/api/admin/toggle-company/${c.id}`);
            alert(`Company ${c.is_active ? 'deactivated' : 'activated'}`);
            this.loadCompanies();
        },
        async generateReport() {
            try {
                await axios.post('/api/admin/trigger-report');
                alert("Report generation is running in background (Celery). Wait 5 seconds and then click 'View Latest Report'.");
            } catch (err) {
                alert("Error triggering report. Check if Redis/Celery is running.");
            }
        }
    },

    mounted() {
        this.loadStats();
        this.loadStudents();
        this.loadCompanies();
        this.loadDrives();
        this.loadPendingCompanies();
        this.loadPendingDrives();
    }
};