// ===============================
// STUDENT DASHBOARD - 
// ===============================

const StudentDashboard = {
    template: `
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Student Dashboard</h2>
            <div>
                <button class="btn btn-outline-primary" :class="{active: tab==='jobs'}" @click="tab='jobs'">Browse Jobs</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='profile'}" @click="tab='profile'">Profile</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='applications'}" @click="tab='applications'">My Applications</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='placements'}" @click="tab='placements'">Placements</button>
            </div>
        </div>
        <div v-if="tab==='jobs'">
            <div class="d-flex justify-content-between mb-3">
                <h4>Available Jobs</h4>
                <div>
                    <input class="form-control" placeholder="Search jobs..." v-model="jobSearch" @input="searchJobs">
                </div>
            </div>
            
            <div class="row">
                <div v-for="j in jobs" :key="j.job_id" class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">[[ j.title ]]</h5>
                            <h6 class="text-muted">[[ j.company ]]</h6>
                            <p><strong>Salary:</strong> [[ j.salary ]] LPA</p>
                            <p><strong>Skills:</strong> [[ j.skills_required ]]</p>
                            <p><strong>Location:</strong> [[ j.location || 'N/A' ]]</p>
                            
                            <div v-if="!checkEligibility(j)" class="alert alert-warning py-1 px-2">
                                <small>You may not meet eligibility criteria</small>
                            </div>
                            
                            <button class="btn w-100" 
                                    :class="hasApplied(j.job_id) ? 'btn-secondary' : 'btn-primary'"
                                    @click="applyJob(j.job_id)"
                                    :disabled="hasApplied(j.job_id) || applying">
                                [[ hasApplied(j.job_id) ? 'Already Applied' : 'Apply Now' ]]
                            </button>
                        </div>
                    </div>
                </div>
                <div v-if="jobs.length===0" class="col-12">
                    <p class="text-muted">No jobs available</p>
                </div>
            </div>
        </div>

        <div v-if="tab==='profile'" class="row">
            <div class="col-md-8 mx-auto">
                <div class="card">
                    <div class="card-header bg-primary text-white">My Profile</div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label>Full Name *</label>
                            <input v-model="profile.name" class="form-control" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label>Branch *</label>
                                <select v-model="profile.branch" class="form-select" required>
                                    <option value="">Select</option>
                                    <option>CSE</option><option>ECE</option><option>ME</option><option>CE</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label>CGPA *</label>
                                <input v-model.number="profile.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label>Skills *</label>
                            <input v-model="profile.skills" class="form-control" placeholder="Python, SQL, JavaScript" required>
                        </div>
                        <div class="mb-3">
                            <label>Education</label>
                            <textarea v-model="profile.education" class="form-control" rows="2" placeholder="B.Tech, 2022-2026, CGPA: 8.5"></textarea>
                        </div>
                        <div class="mb-3">
                            <label>Experience</label>
                            <textarea v-model="profile.experience" class="form-control" rows="2" placeholder="Internships, projects..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label>Resume</label>
                            <div class="input-group">
                                <input type="file" class="form-control" @change="handleResumeUpload" accept=".pdf">
                                <button class="btn btn-outline-secondary" @click="uploadResume" :disabled="!resumeFile">Upload</button>
                            </div>
                            <small v-if="profile.resume" class="text-success">Uploaded: [[ profile.resume ]]</small>
                        </div>
                        <button class="btn btn-success" @click="saveProfile" :disabled="saving">
                            [[ saving ? 'Saving...' : 'Save Profile' ]]
                        </button>
                    </div>
                </div>
            </div>
        </div>

        

        <div v-if="tab==='applications'">
            <div class="d-flex justify-content-between align-items-center mb-2">
            <h4>My Applications</h4>
            <div>
                <button class="btn btn-success btn-sm me-2" @click="exportCSV">
                    Export CSV
                </button>
                <button class="btn btn-outline-primary btn-sm" @click="viewCSV">
                    View CSV
                </button>
            </div>
        </div>
            
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Company</th><th>Position</th><th>Applied On</th>
                        <th>Status</th><th>Interview Date</th><th>Feedback</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="a in applications" :key="a.application_id">
                        <td>[[ a.company ]]</td>
                        <td>[[ a.job_title ]]</td>
                        <td>[[ formatDate(a.applied_on) ]]</td>
                        <td>
                            <span class="badge" :class="{
                                'bg-primary': a.status==='Applied',
                                'bg-success': a.status==='Shortlisted' || a.status==='Selected',
                                'bg-info': a.status==='Interview',
                                'bg-danger': a.status==='Rejected',
                                'bg-dark': a.status==='Placed'
                            }">[[ a.status || 'Applied' ]]</span>
                        </td>
                        <td>[[ a.interview_date ? formatDate(a.interview_date) : 'Not scheduled' ]]</td>
                        <td>[[ a.feedback || 'No feedback' ]]</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="tab==='placements'">
            <h4>My Placement History</h4>
            
            <div class="row">
                <div v-for="p in placements" :key="p.placement_id" class="col-md-6 mb-3">
                    <div class="card border-success">
                        <div class="card-body">
                            <h5>[[ p.company_name ]]</h5>
                            <p><strong>Position:</strong> [[ p.position ]]</p>
                            <p><strong>Salary:</strong> [[ p.salary ]] LPA</p>
                            <p><strong>Joining Date:</strong> [[ formatDate(p.joining_date) ]]</p>
                            <button class="btn btn-sm btn-outline-primary" @click="downloadOfferLetter(p.placement_id)">
                                Download Offer Letter
                            </button>
                        </div>
                    </div>
                </div>
                <div v-if="placements.length===0" class="col-12">
                    <p class="text-muted">No placement records yet</p>
                </div>
            </div>
        </div>
    </div>
    `,

    data() {
        return {
            tab: 'jobs',
            profile: {
                name: '',
                branch: '',
                cgpa: '',
                skills: '',
                education: '',
                experience: '',
                resume: ''
            },
            jobs: [],
            applications: [],
            placements: [],
            appliedJobIds: new Set(),
            jobSearch: '',
            resumeFile: null,
            saving: false,
            applying: false
        };
    },

    methods: {
        async loadProfile() {
            try {
                const res = await axios.get('/api/student/profile');
                this.profile = res.data;
            } catch (err) {
                console.log('Profile not found');
            }
        },

        async saveProfile() {
            this.saving = true;
            try {
                await axios.put('/api/student/update-profile', this.profile);
                alert('Profile saved successfully');
                this.tab = 'jobs';
            } catch (err) {
                alert('Failed to save profile');
            }
            this.saving = false;
        },

        handleResumeUpload(e) {
            this.resumeFile = e.target.files[0];
        },

        async uploadResume() {
            if (!this.resumeFile) return;
            
            const formData = new FormData();
            formData.append('resume', this.resumeFile);
            
            try {
                const res = await axios.post('/api/student/upload-resume', formData);
                this.profile.resume = res.data.resume_url;
                alert('Resume uploaded');
            } catch (err) {
                alert('Upload failed');
            }
        },

        async loadJobs() {
            const params = {};
            if (this.jobSearch) params.q = this.jobSearch;
            
            const res = await axios.get('/api/student/jobs', { params });
            this.jobs = res.data;
        },

        searchJobs() {
            this.loadJobs();
        },

        async loadApplications() {
            const res = await axios.get('/api/student/my-applications');
            this.applications = res.data;
            this.appliedJobIds = new Set(this.applications.map(a => a.job_id));
        },

        async loadPlacements() {
            const res = await axios.get('/api/student/my-placements');
            this.placements = res.data;
        },

        checkEligibility(job) {
            if (!job.eligibility) return true;
            
            const elig = job.eligibility.toLowerCase();
            
            if (elig.includes('cgpa') && this.profile.cgpa) {
                const match = elig.match(/cgpa\s*>\s*(\d+\.?\d*)/);
                if (match && this.profile.cgpa < parseFloat(match[1])) {
                    return false;
                }
            }
            
            if (elig.includes('branch') && this.profile.branch) {
                if (!elig.includes(this.profile.branch.toLowerCase())) {
                    return false;
                }
            }
            
            return true;
        },

        hasApplied(jobId) {
            return this.appliedJobIds.has(jobId);
        },

        async applyJob(jobId) {
            this.applying = true;
            try {
                await axios.post(`/api/student/apply/${jobId}`);
                alert('Application submitted!');
                await this.loadApplications();
            } catch (err) {
                alert(err.response?.data?.message || 'Failed to apply');
            }
            this.applying = false;
        },

        downloadOfferLetter(placementId) {
            window.location.href = `/api/student/offer-letter-html/${placementId}`;
        },
        async exportCSV() {
            try {
                const res = await axios.get('/api/student/export');
                alert('Export started. Please wait a few seconds.');
            } catch (err) {
                alert('Export failed');
            }
        },

        viewCSV() {
            window.open('/api/student/download-export', '_blank');
        },

        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            return new Date(dateStr).toLocaleDateString();
        }    
    },
    watch: {
        tab(newTab) {
            if (newTab === 'applications') {
                this.loadApplications()
            }
        }
    },

    mounted() {
        this.loadProfile();
        this.loadJobs();
        this.loadApplications();
        this.loadPlacements();
    }
};