/* ============================================
   SMART FOOD ANALYSIS — Main Script
   SPA Routing + Upload + API + Animations
   ============================================ */

// ---- SPA ROUTING ----
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('.nav-link');
const navToggle = document.getElementById('nav-toggle');
const navLinksContainer = document.getElementById('nav-links');
const navbar = document.getElementById('navbar');

function navigateTo(pageId) {
    pages.forEach(p => p.classList.remove('active'));
    navLinks.forEach(l => l.classList.remove('active'));

    const target = document.getElementById('page-' + pageId);
    if (target) {
        target.classList.add('active');
    }
    
    navLinks.forEach(l => {
        if (l.dataset.page === pageId) l.classList.add('active');
    });

    // Close mobile menu
    navLinksContainer.classList.remove('open');

    // Scroll to top on page change
    window.scrollTo({ top: 0 });

    // Re-trigger reveal animations for the new page
    initRevealAnimations();
}

function handleHashChange() {
    const hash = window.location.hash.replace('#', '') || 'intro';

    if(hash === 'profile' || hash === 'admin') {
        const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
        if(!loggedUser) {
            window.location.hash = 'intro';
            return;
        }
        if(hash === 'admin' && loggedUser.role !== 'admin') {
            window.location.hash = 'intro';
            return;
        }
    }

    navigateTo(hash);
    
    if(hash === 'profile') {
        initProfilePage();
    } else if (hash === 'admin') {
        initAdminPage();
    }
}

window.addEventListener('hashchange', handleHashChange);
window.addEventListener('DOMContentLoaded', handleHashChange);

// Nav link clicks
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        // Let the hash change handle page switching
        const page = link.dataset.page;
        if (page) {
            window.location.hash = page;
        }
    });
});

// Hero CTA button
const heroCta = document.getElementById('hero-cta');
if (heroCta) {
    heroCta.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.hash = 'analyze';
    });
}

// Mobile toggle
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navLinksContainer.classList.toggle('open');
    });
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ---- SCROLL REVEAL ANIMATIONS ----
function initRevealAnimations() {
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(el => {
        el.classList.remove('visible');
        observer.observe(el);
    });
}

// ---- UPLOAD & ANALYSIS LOGIC ----
function initAnalyzePage() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.getElementById('upload-content');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('preview-img');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');

    if (!dropZone) return;

    let currentFile = null;

    // Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-active'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-active'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            currentFile = files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                uploadContent.classList.add('hidden');
                previewContainer.classList.remove('hidden');
                resultSection.classList.add('hidden');
            };
            reader.readAsDataURL(currentFile);
        }
    }

    removeBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        previewImg.src = '';
        uploadContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        resultSection.classList.add('hidden');
    });

    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // Show loading
        previewContainer.classList.add('hidden');
        loading.classList.remove('hidden');
        resultSection.classList.add('hidden');
        
        let loaderText = loading.querySelector('.loader-text');
        if (loaderText) {
            loaderText.innerHTML = 'AI đang nhận diện hình ảnh<span class="dots"></span>';
        }
        
        // Progressively update loading text if it takes longer than 3 seconds (AI Generation)
        let loadingTimer = setTimeout(() => {
            if (loaderText) {
                loaderText.innerHTML = 'Nhận diện thấy món ăn mới. Đang nhờ AI phân tích công thức, vui lòng chờ...';
            }
        }, 4000);

        const formData = new FormData();
        formData.append('file', currentFile);
        
        const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
        if (loggedUser) {
            formData.append('user_id', loggedUser.id);
        }

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            clearTimeout(loadingTimer);
            loading.classList.add('hidden');
            previewContainer.classList.remove('hidden');

            if (data.success) {
                showResult(data);
            } else {
                showError(data.message || 'Lỗi từ Backend Server!');
            }

        } catch (err) {
            console.error('Fetch error:', err);
            clearTimeout(loadingTimer);
            loading.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            showError('Lỗi kết nối tới Server. Đảm bảo Backend đang chạy.');
        }
    });
}

function showResult(data) {
    const resultSection = document.getElementById('result-section');
    const sysMsg = document.getElementById('sys-msg');

    resultSection.classList.remove('hidden');
    sysMsg.textContent = '';
    sysMsg.classList.remove('visible');

    document.getElementById('confidence-score').textContent = data.confidence;

    if (data.food_data) {
        document.getElementById('food-name').textContent = data.food_data.name;
        document.getElementById('food-desc').textContent = data.food_data.description || 'Chưa có thông tin mô tả chi tiết.';
        document.getElementById('val-cal').textContent = data.food_data.calories;
        document.getElementById('val-prot').textContent = data.food_data.proteins;
        document.getElementById('val-carb').textContent = data.food_data.carbs;
        document.getElementById('val-fat').textContent = data.food_data.fats;

        // Recipe & Ingredients
        const recipeContainer = document.getElementById('recipe-container');
        const ingredientsList = document.getElementById('ingredients-list');
        const recipeInstructions = document.getElementById('recipe-instructions');
        const recipeTime = document.getElementById('recipe-time');

        if (data.food_data.recipe_instructions || (data.food_data.ingredients && data.food_data.ingredients.length > 0)) {
            recipeContainer.classList.remove('hidden');
            ingredientsList.innerHTML = '';

            if (data.food_data.ingredients && data.food_data.ingredients.length > 0) {
                data.food_data.ingredients.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = `${item.TenNguyenLieu} — ${item.SoLuong}`;
                    ingredientsList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'Đang cập nhật...';
                ingredientsList.appendChild(li);
            }

            recipeInstructions.textContent = data.food_data.recipe_instructions || 'Đang cập nhật công thức...';

            if (data.food_data.recipe_time) {
                recipeTime.textContent = `⏱ ${data.food_data.recipe_time} phút`;
            } else {
                recipeTime.textContent = '';
            }
        } else {
            recipeContainer.classList.add('hidden');
        }
    } else {
        // API recognized but no DB match
        document.getElementById('food-name').textContent = data.predicted_class_name || 'Không xác định';
        document.getElementById('food-desc').textContent = 'Dữ liệu sơ bộ từ AI (Chưa có dữ liệu ánh xạ món ăn này trong Database).';

        if (data.message) {
            sysMsg.textContent = data.message;
            sysMsg.classList.add('visible');
        }

        ['val-cal', 'val-prot', 'val-carb', 'val-fat'].forEach(id => {
            document.getElementById(id).textContent = '--';
        });
        document.getElementById('recipe-container').classList.add('hidden');
    }

    // Scroll result into view
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    const sysMsg = document.getElementById('sys-msg');
    const resultSection = document.getElementById('result-section');

    resultSection.classList.remove('hidden');
    document.getElementById('food-name').textContent = 'Lỗi Phân Tích';
    document.getElementById('food-desc').textContent = message;
    document.getElementById('confidence-score').textContent = '0';

    sysMsg.textContent = message;
    sysMsg.classList.add('visible');

    ['val-cal', 'val-prot', 'val-carb', 'val-fat'].forEach(id => {
        document.getElementById(id).textContent = '--';
    });
    document.getElementById('recipe-container').classList.add('hidden');
}

// ---- AUTH LOGIC ----
function checkLoginState() {
    const authSection = document.getElementById('auth-section');
    const userSection = document.getElementById('user-section');
    const userNameDisplay = document.getElementById('user-name-display');
    const navAdminLink = document.getElementById('nav-admin-link');
    
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    
    if (loggedUser) {
        if(authSection) authSection.classList.add('hidden');
        if(userSection) userSection.classList.remove('hidden');
        if(userNameDisplay) {
            userNameDisplay.innerHTML = `<i class="fa-solid fa-user"></i> ${loggedUser.name}`;
            userNameDisplay.style.cursor = 'pointer';
        }
        if(navAdminLink) {
            if(loggedUser.role === 'admin') navAdminLink.classList.remove('hidden');
            else navAdminLink.classList.add('hidden');
        }
    } else {
        if(authSection) authSection.classList.remove('hidden');
        if(userSection) userSection.classList.add('hidden');
        if(navAdminLink) navAdminLink.classList.add('hidden');
    }
}

function initAuth() {
    const modalOverlay = document.getElementById('auth-modal');
    const loginBox = document.getElementById('login-box');
    const registerBox = document.getElementById('register-box');
    
    // Shows
    document.getElementById('btn-show-login')?.addEventListener('click', () => {
        modalOverlay.classList.remove('hidden');
        loginBox.classList.remove('hidden');
        registerBox.classList.add('hidden');
    });
    
    document.getElementById('btn-show-register')?.addEventListener('click', () => {
        modalOverlay.classList.remove('hidden');
        registerBox.classList.remove('hidden');
        loginBox.classList.add('hidden');
    });
    
    // Switch
    document.getElementById('switch-to-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        loginBox.classList.add('hidden');
        registerBox.classList.remove('hidden');
    });
    
    document.getElementById('switch-to-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        registerBox.classList.add('hidden');
        loginBox.classList.remove('hidden');
    });
    
    // Close
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            modalOverlay.classList.add('hidden');
        });
    });
    
    // Forms
    const loginForm = document.getElementById('login-form');
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errDiv = document.getElementById('login-error');
        errDiv.classList.add('hidden');
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            
            if (data.success) {
                localStorage.setItem('smartfood_user', JSON.stringify(data.user));
                modalOverlay.classList.add('hidden');
                checkLoginState();
                loginForm.reset();
            } else {
                errDiv.textContent = data.message;
                errDiv.classList.remove('hidden', 'success');
            }
        } catch (error) {
            errDiv.textContent = "Lỗi kết nối máy chủ";
            errDiv.classList.remove('hidden', 'success');
        }
    });

    const regForm = document.getElementById('register-form');
    regForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errDiv = document.getElementById('reg-error');
        errDiv.classList.add('hidden');
        
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        
        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();
            
            if (data.success) {
                errDiv.textContent = data.message + " - Vui lòng đăng nhập.";
                errDiv.classList.remove('hidden');
                errDiv.classList.add('success');
                regForm.reset();
                setTimeout(() => {
                    document.getElementById('switch-to-login').click();
                    errDiv.classList.add('hidden');
                }, 1500);
            } else {
                errDiv.textContent = data.message;
                errDiv.classList.remove('hidden', 'success');
            }
        } catch (error) {
            errDiv.textContent = "Lỗi kết nối máy chủ";
            errDiv.classList.remove('hidden', 'success');
        }
    });
    
    // Logout
    document.getElementById('btn-logout')?.addEventListener('click', () => {
        localStorage.removeItem('smartfood_user');
        checkLoginState();
    });}

// ---- PROFILE LOGIC ----
async function initProfilePage() {
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    if (!loggedUser) return;

    // Set UI Info
    const nameEl = document.getElementById('profile-page-name');
    const emailEl = document.getElementById('profile-page-email');
    if (nameEl) nameEl.textContent = loggedUser.name;
    if (emailEl) emailEl.textContent = loggedUser.email;

    // Load History
    const historyContainer = document.getElementById('history-container');
    if(historyContainer) {
        try {
            historyContainer.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px 0;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p style="margin-top: 10px;">Đang tải lịch sử...</p></div>';
            
            const res = await fetch('/api/history/' + loggedUser.id);
            const data = await res.json();
            
            if (data.success && data.history && data.history.length > 0) {
                historyContainer.innerHTML = '';
                data.history.forEach(item => {
                    const el = document.createElement('div');
                    el.style.cssText = "background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center;";
                    
                    const date = item.ThoiGianNhanDien ? new Date(item.ThoiGianNhanDien).toLocaleString() : '';
                    
                    el.innerHTML = `
                        <div>
                            <h4 style="font-size: 16px; margin-bottom: 4px; font-weight: 600; color: var(--primary-light);">${item.KetQuaNhanDien}</h4>
                            <p style="font-size: 12px; color: var(--text-muted);"><i class="fa-regular fa-clock"></i> ${date}</p>
                        </div>
                        <div style="background: rgba(163, 230, 53, 0.15); color: var(--c-carb); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                            ${item.DoChinhXac}%
                        </div>
                    `;
                    historyContainer.appendChild(el);
                });
            } else {
                historyContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted); margin-top: 20px;">Chưa có lịch sử tra cứu nào.</p>';
            }
        } catch (e) {
            historyContainer.innerHTML = '<p style="text-align: center; color: var(--c-fat); margin-top: 20px;">Lỗi tải dữ liệu.</p>';
        }
    }

    // Handlers (only attach once)
    const pwForm = document.getElementById('change-pw-form');
    if (pwForm && !pwForm.dataset.initialized) {
        pwForm.dataset.initialized = 'true';
        pwForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errDiv = document.getElementById('pw-error');
            errDiv.classList.add('hidden');
            
            const oldPw = document.getElementById('pw-old').value;
            const newPw = document.getElementById('pw-new').value;
            
            try {
                const res = await fetch('/api/change-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: loggedUser.id, old_password: oldPw, new_password: newPw })
                });
                const responseData = await res.json();
                
                if (responseData.success) {
                    errDiv.textContent = responseData.message;
                    errDiv.classList.remove('hidden');
                    errDiv.classList.add('success');
                    pwForm.reset();
                    setTimeout(() => errDiv.classList.add('hidden'), 3000);
                } else {
                    errDiv.textContent = responseData.message;
                    errDiv.classList.remove('hidden', 'success');
                }
            } catch (err) {
                errDiv.textContent = 'Lỗi kết nối';
                errDiv.classList.remove('hidden', 'success');
            }
        });
    }

    const btnPageLogout = document.getElementById('btn-page-logout');
    if (btnPageLogout && !btnPageLogout.dataset.initialized) {
        btnPageLogout.dataset.initialized = 'true';
        btnPageLogout.addEventListener('click', () => {
            localStorage.removeItem('smartfood_user');
            checkLoginState();
            window.location.hash = 'intro';
        });
    }
}

// ---- ADMIN LOGIC ----
async function initAdminPage() {
    console.log("initAdminPage called!");
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    if (!loggedUser || loggedUser.role !== 'admin') {
        console.log("Not admin, exiting initAdminPage");
        return;
    }

    // Tabs logic (only initialize once)
    const adminPage = document.getElementById('page-admin');
    console.log("Admin page initialized flag:", adminPage?.dataset?.initialized);
    
    if(adminPage && !adminPage.dataset.initialized) {
        console.log("Initializing admin page logic...");
        adminPage.dataset.initialized = 'true';
        
        const tabs = document.querySelectorAll('.admin-tab');
        const contents = document.querySelectorAll('.admin-tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.add('hidden'));
                
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.remove('hidden');
                
                // Refresh data if needed based on tab activated
                if(tab.dataset.tab === 'admin-stats') fetchAdminStats();
                if(tab.dataset.tab === 'admin-foods') fetchAdminFoods();
                if(tab.dataset.tab === 'admin-users') fetchAdminUsers();
                if(tab.dataset.tab === 'admin-history') fetchAdminHistory();
            });
        });

        // Food Modal Logic
        const btnAddFood = document.getElementById('btn-admin-add-food');
        const adminModalOverlay = document.getElementById('admin-modal-overlay');
        const foodForm = document.getElementById('food-admin-form');
        const btnAddIng = document.getElementById('fa-add-ing');
        const ingsContainer = document.getElementById('fa-ingredients');

        console.log("Found modal elements:", { btnAddFood, adminModalOverlay, foodForm });

        btnAddFood.addEventListener('click', () => {
            console.log("Thêm Món clicked!");
            foodForm.reset();
            document.getElementById('fa-id').value = '';
            document.getElementById('food-modal-title').textContent = 'Thêm Món Ăn';
            ingsContainer.innerHTML = ''; // clear ingredients
            addIngredientRow('');
            adminModalOverlay.classList.remove('hidden');
        });

        btnAddIng.addEventListener('click', () => {
            addIngredientRow('');

        });

        function addIngredientRow(value) {
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.gap = '10px';
            
            const [name, qty] = value.split(' — ');
            
            row.innerHTML = `
                <input type="text" class="form-input ing-name" placeholder="Tên nguyên liệu..." style="flex: 2" value="${name || ''}">
                <input type="text" class="form-input ing-qty" placeholder="Số lượng..." style="flex: 1" value="${qty || ''}">
                <button type="button" class="btn-icon delete" onclick="this.parentElement.remove()"><i class="fa-solid fa-trash"></i></button>
            `;
            ingsContainer.appendChild(row);
        }

        foodForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errDiv = document.getElementById('fa-error');
            errDiv.classList.add('hidden');

            const id = document.getElementById('fa-id').value;
            
            const ings = [];
            ingsContainer.querySelectorAll('div').forEach(row => {
                const n = row.querySelector('.ing-name').value.trim();
                const q = row.querySelector('.ing-qty').value.trim();
                if(n) ings.push({ TenNguyenLieu: n, SoLuong: q });
            });

            const data = {
                TenMonAn: document.getElementById('fa-name').value,
                PhanLoai: document.getElementById('fa-cate').value,
                MoTa: document.getElementById('fa-desc').value,
                IsDeleted: document.getElementById('fa-deleted').value,
                DinhDuong: {
                    Calo: document.getElementById('fa-cal').value || 0,
                    Protein: document.getElementById('fa-pro').value || 0,
                    ChatBeo: document.getElementById('fa-fat').value || 0,
                    Carbohydrate: document.getElementById('fa-car').value || 0,
                    Vitamin: ''
                },
                CongThuc: {
                    HuongDan: document.getElementById('fa-instruct').value,
                    ThoiGianNau: 30, // Default estimate
                    KhauPhan: 1,
                    NguyenLieu: ings
                }
            };

            try {
                const url = id ? `/api/admin/foods/${id}` : '/api/admin/foods';
                const method = id ? 'PUT' : 'POST';
                
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const responseData = await res.json();
                if(responseData.success) {
                    adminModalOverlay.classList.add('hidden');
                    fetchAdminFoods();
                } else {
                    errDiv.textContent = responseData.message || 'Lỗi lưu dữ liệu';
                    errDiv.classList.remove('hidden', 'success');
                }
            } catch(error) {
                errDiv.textContent = 'Lỗi kết nối máy chủ';
                errDiv.classList.remove('hidden', 'success');
            }
        });

        // Global Edit/Delete Handlers
        window.editAdminFood = async (id) => {
            try {
                const res = await fetch(`/api/admin/foods/${id}`);
                const responseData = await res.json();
                if(responseData.success) {
                    const f = responseData.food;
                    document.getElementById('fa-id').value = f.MaMonAn;
                    document.getElementById('fa-name').value = f.TenMonAn || '';
                    document.getElementById('fa-cate').value = f.PhanLoai || '';
                    document.getElementById('fa-desc').value = f.MoTa || '';
                    document.getElementById('fa-deleted').value = f.IsDeleted || 0;
                    
                    if(f.DinhDuong) {
                        document.getElementById('fa-cal').value = f.DinhDuong.Calo || '';
                        document.getElementById('fa-pro').value = f.DinhDuong.Protein || '';
                        document.getElementById('fa-fat').value = f.DinhDuong.ChatBeo || '';
                        document.getElementById('fa-car').value = f.DinhDuong.Carbohydrate || '';
                    } else {
                        document.getElementById('fa-cal').value = '';
                        document.getElementById('fa-pro').value = '';
                        document.getElementById('fa-fat').value = '';
                        document.getElementById('fa-car').value = '';
                    }
                    
                    if(f.CongThuc) {
                        document.getElementById('fa-instruct').value = f.CongThuc.HuongDan || '';
                        ingsContainer.innerHTML = '';
                        if(f.CongThuc.NguyenLieu && f.CongThuc.NguyenLieu.length > 0) {
                            f.CongThuc.NguyenLieu.forEach(nl => {
                                addIngredientRow(`${nl.TenNguyenLieu} — ${nl.SoLuong}`);
                            });
                        } else {
                            addIngredientRow('');
                        }
                    } else {
                        document.getElementById('fa-instruct').value = '';
                        ingsContainer.innerHTML = '';
                        addIngredientRow('');
                    }

                    document.getElementById('food-modal-title').textContent = 'Sửa Món Ăn (ID: ' + id + ')';
                    adminModalOverlay.classList.remove('hidden');
                } else {
                    alert("Không tải được chi tiết món ăn!");
                }
            } catch(e) { console.error(e); alert("Lỗi kết nối máy chủ."); }
        };

        window.deleteAdminFood = async (id) => {
            if(!confirm('Bạn có chắc chắn muốn CHUYỂN VÀO THÙNG RÁC món ăn này? (Sẽ không còn hiện trên web cho User)')) return;
            try {
                const res = await fetch(`/api/admin/foods/${id}`, { method: 'DELETE' });
                const r = await res.json();
                if(r.success) fetchAdminFoods();
                else alert(r.message);
            } catch(e) { console.error(e); }
        };

        window.restoreAdminFood = async (id) => {
            if(!confirm('Bạn muốn HOÀN TÁC (khôi phục) món ăn này để hiển thị lại trên web?')) return;
            try {
                const res = await fetch(`/api/admin/foods/${id}/restore`, { method: 'PUT' });
                const r = await res.json();
                if(r.success) fetchAdminFoods();
                else alert(r.message);
            } catch(e) { console.error(e); }
        };

        window.deleteAdminUser = async (id) => {
            if(!confirm('Bạn có chắc chắn muốn XÓA VĨNH VIỄN người dùng này?')) return;
            try {
                const res = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
                const r = await res.json();
                if(r.success) fetchAdminUsers();
                else alert(r.message);
            } catch(e) { console.error(e); }
        };
    }

    // Default fetch on load
    fetchAdminStats();

    // Fetch Functions
    async function fetchAdminStats() {
        try {
            const res = await fetch('/api/admin/stats');
            const data = await res.json();
            if(data.success) {
                document.getElementById('st-users').textContent = data.stats.total_users;
                document.getElementById('st-foods').textContent = data.stats.total_foods;
                document.getElementById('st-recs').textContent = data.stats.total_recognitions;
            }
        } catch(e) { console.error(e); }
    }

    async function fetchAdminFoods() {
        const tb = document.getElementById('tb-foods');
        tb.innerHTML = '<tr><td colspan="5" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/foods');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.foods.forEach(f => {
                    const status = f.IsDeleted ? '<span class="badge badge-danger">Đã khóa</span>' : '<span class="badge badge-success">Hiển thị</span>';
                    tb.innerHTML += `
                        <tr>
                            <td>#${f.MaMonAn}</td>
                            <td>${f.TenMonAn}</td>
                            <td>${f.PhanLoai}</td>
                            <td>${status}</td>
                            <td>
                                <div class="action-btns">
                                    <button class="btn-icon" title="Sửa" onclick="editAdminFood(${f.MaMonAn})"><i class="fa-solid fa-pen"></i></button>
                                    ${!f.IsDeleted ? `<button class="btn-icon delete" title="Khóa" onclick="deleteAdminFood(${f.MaMonAn})"><i class="fa-solid fa-ban"></i></button>` : `<button class="btn-icon" title="Hoàn tác" style="color: var(--c-carb);" onclick="restoreAdminFood(${f.MaMonAn})"><i class="fa-solid fa-rotate-left"></i></button>`}
                                </div>
                            </td>
                        </tr>
                    `;
                });
            }
        } catch(e) { console.error(e); tb.innerHTML = '<tr><td colspan="5" style="text-align:center; color:red;">Lỗi tải dữ liệu</td></tr>'; }
    }

    async function fetchAdminUsers() {
        const tb = document.getElementById('tb-users');
        tb.innerHTML = '<tr><td colspan="6" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/users');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.users.forEach(u => {
                    const status = u.VaiTro === 'admin' ? '<span class="badge badge-warning"><i class="fa-solid fa-star"></i> Admin</span>' : '<span class="badge badge-info">User</span>';
                    tb.innerHTML += `
                        <tr>
                            <td>#${u.MaNguoiDung}</td>
                            <td style="font-weight: 500">${u.TenNguoiDung}</td>
                            <td>${u.Email}</td>
                            <td>${status}</td>
                            <td>${u.NgayDangKy}</td>
                            <td>
                                <div class="action-btns">
                                    <button class="btn-icon delete" title="Xóa" onclick="deleteAdminUser(${u.MaNguoiDung})"><i class="fa-solid fa-trash"></i></button>
                                </div>
                            </td>
                        </tr>
                    `;
                });
            }
        } catch(e) { console.error(e); }
    }

    async function fetchAdminHistory() {
        const tb = document.getElementById('tb-history');
        tb.innerHTML = '<tr><td colspan="5" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/history');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.history.forEach(h => {
                    tb.innerHTML += `
                        <tr>
                            <td>#${h.MaLichSu}</td>
                            <td>${h.TenNguoiDung ? h.TenNguoiDung + ' <i>('+h.Email+')</i>' : 'Khách'}</td>
                            <td style="font-weight:500; color:var(--primary-light)">${h.KetQuaNhanDien}</td>
                            <td><span class="badge badge-success">${h.DoChinhXac}%</span></td>
                            <td><span style="font-size: 13px; color: var(--text-muted);">${new Date(h.ThoiGianNhanDien).toLocaleString()}</span></td>
                        </tr>
                    `;
                });
            }
        } catch(e) { console.error(e); }
    }
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    checkLoginState();
    initAnalyzePage();
    initRevealAnimations();
});
