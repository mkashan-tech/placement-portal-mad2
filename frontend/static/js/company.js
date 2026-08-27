// ===============================
// COMPANY DASHBOARD - 
// ===============================

const CompanyDashboard = {
    template: `
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Company Dashboard</h2>
            <div>
                <button class="btn btn-outline-primary" :class="{active: tab==='dashboard'}" @click="tab='dashboard'">Dashboard</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='jobs'}" @click="tab='jobs'">My Jobs</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='post'}" @click="tab='post'">Post Job</button>
                <button class="btn btn-outline-primary" :class="{active: tab==='applicants'}" @click="tab='applicants'">Applicants</button>
            </div>
        </div>

        <div v-if="!isApproved" class="alert alert-warning">
            Your company is pending admin approval. Jobs you post will be visible only after approval.
        </div>

        <div v-if="tab==='dashboard'" class="row">
            <div class="col-md-3">
                <div class="card text-center p-3">
                    <h6>Total Jobs</h6>
                    <h3>[[ dashboardStats.total_jobs || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center p-3">
                    <h6>Active Jobs</h6>
                    <h3>[[ dashboardStats.active_jobs || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center p-3">
                    <h6>Applications</h6>
                    <h3>[[ dashboardStats.total_applications || 0 ]]</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center p-3">
                    <h6>Shortlisted</h6>
                    <h3>[[ dashboardStats.shortlisted_count || 0 ]]</h3>
                </div>
            </div>
        </div>

        <div v-if="tab==='jobs'">
            <h4>My Job Postings</h4>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Title</th><th>Salary</th><th>Location</th>
                        <th>Status</th><th>Approval</th><th>Applicants</th><th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="j in jobs" :key="j.id">
                        <td>[[ j.title ]]</td>
                        <td> [[ j.salary ]] LPA</td>
                        <td>[[ j.location || 'N/A' ]]</td>
                        <td>
                            <span class="badge" :class="{
                                'bg-success': j.status==='Active',
                                'bg-warning': j.status==='Pending',
                                'bg-secondary': j.status==='Closed'
                            }">[[ j.status ]]</span>
                        </td>
                        <td>
                            <span class="badge" :class="j.approved ? 'bg-success' : 'bg-warning'">
                                [[ j.approved ? 'Approved' : 'Pending' ]]
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="viewApplicants(j.id)">[[ j.applicants_count || 0 ]] View</button>
                        </td>
                        <td>
                            <button v-if="j.status!=='Closed'" class="btn btn-sm btn-warning" @click="closeJob(j.id)">Close</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="tab==='post'" class="row">
            <div class="col-md-8 mx-auto">
                <div class="card">
                    <div class="card-header">Post New Job / Placement Drive</div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label>Job Title *</label>
                            <input v-model="newJob.title" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label>Description *</label>
                            <textarea v-model="newJob.description" class="form-control" rows="3" required></textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label>Salary (LPA) *</label>
                                <input v-model.number="newJob.salary" type="number" step="0.1" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label>Location</label>
                                <input v-model="newJob.location" class="form-control">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label>Skills Required *</label>
                            <input v-model="newJob.skills_required" class="form-control" placeholder="Python, SQL, JavaScript" required>
                        </div>
                        <div class="mb-3">
                            <label>Experience Required</label>
                            <input v-model="newJob.experience_required" class="form-control" placeholder="e.g., 0-2 years">
                        </div>
                        <div class="mb-3">
                            <label>Eligibility Criteria</label>
                            <input v-model="newJob.eligibility" class="form-control" placeholder="e.g., CGPA > 7, CSE only">
                        </div>
                        <div class="mb-3">
                            <label>Benefits</label>
                            <textarea v-model="newJob.benefits" class="form-control" rows="2"></textarea>
                        </div>
                        <button class="btn btn-success" @click="submitJob" :disabled="submitting">
                            [[ submitting ? 'Posting...' : 'Post Job' ]]
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="tab==='applicants' && !selectedJob" class="text-center text-muted py-5">
            <p>Select a job from the <strong>My Jobs</strong> tab to view its applicants.</p>
            <button class="btn btn-outline-primary btn-sm" @click="tab='jobs'">Go to My Jobs</button>
        </div>

        <div v-if="tab==='applicants' && selectedJob">
            <div class="d-flex justify-content-between mb-3">
                <h4>Applicants for: [[ selectedJob.title ]]</h4>
                <button class="btn btn-secondary btn-sm" @click="tab='jobs'">← Back</button>
            </div>
            
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Student</th><th>Branch</th><th>CGPA</th>
                        <th>Profile</th><th>Status</th><th>Interview Date</th><th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="a in applicants" :key="a.application_id">
                        <td>[[ a.student_name ]]</td>
                        <td>[[ a.branch ]]</td>
                        <td>[[ a.cgpa ]]</td>
                        <td>
                            <button class="btn btn-sm btn-info" @click="viewStudentProfile(a.student_id)">View</button>
                        </td>
                        <td>
                            <span class="badge" :class="{
                                'bg-primary': a.status==='Applied',
                                'bg-success': a.status==='Shortlisted' || a.status==='Selected' || a.status==='Placed',
                                'bg-info': a.status==='Interview',
                                'bg-danger': a.status==='Rejected'
                            }">[[ a.status ]]</span>
                        </td>
                        <td>
                            <input type="datetime-local" class="form-control form-control-sm" 
                                   v-model="a.interview_date" 
                                   :disabled="a.status==='Placed' || a.status==='Rejected'"
                                   @change="scheduleInterview(a.application_id, a.interview_date)">
                        </td>
                        <td>
                            <select 
                                class="form-select form-select-sm"
                                :disabled="a.status==='Placed'"
                                @change="updateStatus(a, $event.target.value)"
                            >
                                <option value="">Change Status</option>
                                <option value="Shortlisted">Shortlist</option>
                                <option value="Interview">Schedule Interview</option>
                                <option value="Selected">Select & Finalize</option>
                                <option value="Rejected">Reject</option>
                            </select>
                            <textarea v-if="a.status==='Rejected'" class="form-control form-control-sm mt-1" 
                                      placeholder="Feedback" v-model="a.feedback" @blur="saveFeedback(a)"></textarea>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div v-if="showProfileModal" class="modal fade show" style="display:block; background:rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5>Student Profile: [[ profileStudent.name ]]</h5>
                        <button type="button" class="btn-close" @click="showProfileModal=false"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Branch:</strong> [[ profileStudent.branch ]]</p>
                        <p><strong>CGPA:</strong> [[ profileStudent.cgpa ]]</p>
                        <p><strong>Skills:</strong> [[ profileStudent.skills ]]</p>
                        <p><strong>Education:</strong> [[ profileStudent.education ]]</p>
                        <p><strong>Experience:</strong> [[ profileStudent.experience ]]</p>
                        <p><strong>Email:</strong> [[ profileStudent.email ]]</p>
                        <p v-if="profileStudent.resume">
                            <strong>Resume:</strong>
                            <a :href="profileStudent.resume" target="_blank" class="btn btn-sm btn-outline-primary">
                                Download Resume
                            </a>
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
            jobs: [],
            applicants: [],
            selectedJob: null,
            dashboardStats: {},
            isApproved: false,
            submitting: false,
            showProfileModal: false,
            profileStudent: {},
            newJob: {
                title: '',
                description: '',
                salary: '',
                location: '',
                skills_required: '',
                experience_required: '',
                eligibility: '',
                benefits: ''
            }
        };
    },

    methods: {
        async loadDashboard() {
            const res = await axios.get('/api/company/dashboard');
            this.dashboardStats = res.data;
            this.isApproved = res.data.is_approved;
        },

        async loadJobs() {
            const res = await axios.get('/api/company/view-jobs');
            this.jobs = res.data.jobs;        
            this.isApproved = res.data.company_approved;
        },

        async submitJob() {
            this.submitting = true;
            try {
                await axios.post('/api/company/create-job', this.newJob);
                alert('Job posted successfully! Waiting for admin approval.');
                this.newJob = { title: '', description: '', salary: '', location: '', skills_required: '', experience_required: '', eligibility: '', benefits: '' };
                this.loadJobs();
                this.tab = 'jobs';
            } catch (err) {
                alert('Failed to post job');
            }
            this.submitting = false;
        },

        async viewApplicants(jobId) {
            this.selectedJob = this.jobs.find(j => j.id === jobId);
            const res = await axios.get(`/api/company/applicants/${jobId}`);
            this.applicants = res.data.applicants;
            this.tab = 'applicants';
        },

        async viewStudentProfile(studentId) {
            const res = await axios.get(`/api/company/student-profile/${studentId}/${this.selectedJob.id}`);
            this.profileStudent = res.data;
            this.showProfileModal = true;
        },

        async updateStatus(applicant, newStatus) {
            if (!newStatus) return;

            try {
                let payload = { status: newStatus };

                if (newStatus === 'Selected') {
                    const date = prompt('Enter joining date (YYYY-MM-DD):');
                    if (!date) {
                        alert('Joining date required');
                        return;
                    }
                    payload.joining_date = date;
                }

                await axios.put(
                    `/api/company/update-application/${applicant.application_id}`,
                    payload
                );

                alert(`Status updated to ${newStatus}`);

                const res = await axios.get(
                    `/api/company/applicants/${this.selectedJob.id}`
                );
                this.applicants = res.data.applicants;

            } catch (err) {
                alert(err.response?.data?.message || 'Failed to update status');
            }
        },
        async scheduleInterview(appId, dateTime) {
            if (!dateTime) return;
            
            try {
                await axios.put(`/api/company/update-application/${appId}`, {
                    interview_date: dateTime,
                    status: 'Interview'
                });
                
                alert('Interview scheduled. Email reminder will be sent to student.');
                
                // Refresh applicants
                const res = await axios.get(`/api/company/applicants/${this.selectedJob.id}`);
                this.applicants = res.data.applicants; 
                
            } catch (err) {
                alert('Failed to schedule interview');
            }
        },

        async saveFeedback(applicant) {
            if (!applicant.feedback) return;
            
            await axios.put(`/api/company/update-application/${applicant.application_id}`, {
                feedback: applicant.feedback
            });
        },

        async closeJob(jobId) {
            if (confirm('Close this job? Students will not be able to apply.')) {
                await axios.put(`/api/company/close-job/${jobId}`);
                this.loadJobs();
            }
        }
    },

    mounted() {
        this.loadDashboard();
        this.loadJobs();
    }
};