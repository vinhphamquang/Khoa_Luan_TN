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

    if(hash === 'profile') {
        const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
        if(!loggedUser) {
            window.location.hash = 'intro';
            return;
        }
    }

    navigateTo(hash);
    
    if(hash === 'profile') {
        initProfilePage();
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

// ---- FOOD BANNER SLIDER ----
function initFoodSlider() {
    const sliderTrack = document.getElementById('slider-track');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('slider-prev');
    const nextBtn = document.getElementById('slider-next');
    const dots = document.querySelectorAll('.dot');
    
    if (!sliderTrack || slides.length === 0) return;
    
    let currentSlide = 0;
    const totalSlides = slides.length;
    let autoSlideInterval;
    
    function goToSlide(index) {
        // Remove active class from all slides
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        // Add active class to current slide
        currentSlide = index;
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
        
        // Move slider track
        sliderTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
    }
    
    function nextSlide() {
        const next = (currentSlide + 1) % totalSlides;
        goToSlide(next);
    }
    
    function prevSlide() {
        const prev = (currentSlide - 1 + totalSlides) % totalSlides;
        goToSlide(prev);
    }
    
    function startAutoSlide() {
        autoSlideInterval = setInterval(nextSlide, 5000); // Change slide every 5 seconds
    }
    
    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }
    
    // Event listeners
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextSlide();
            stopAutoSlide();
            startAutoSlide(); // Restart auto slide after manual interaction
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            prevSlide();
            stopAutoSlide();
            startAutoSlide();
        });
    }
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            goToSlide(index);
            stopAutoSlide();
            startAutoSlide();
        });
    });
    
    // Pause auto slide on hover
    sliderTrack.addEventListener('mouseenter', stopAutoSlide);
    sliderTrack.addEventListener('mouseleave', startAutoSlide);
    
    // Start auto slide
    startAutoSlide();
}

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
    let stream = null;
    let currentMode = 'upload'; // 'upload' or 'camera'

    const modeUploadBtn = document.getElementById('mode-upload-btn');
    const modeCameraBtn = document.getElementById('mode-camera-btn');
    const cameraSection = document.getElementById('camera-section');
    const cameraVideo = document.getElementById('camera-video');
    const cameraCanvas = document.getElementById('camera-canvas');
    const captureBtn = document.getElementById('capture-btn');

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }

    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            cameraVideo.srcObject = stream;
        } catch (err) {
            console.error("Camera error:", err);
            alert("Không thể truy cập Camera. Vui lòng kiểm tra quyền truy cập.");
            if (modeUploadBtn) modeUploadBtn.click();
        }
    }

    modeUploadBtn?.addEventListener('click', () => {
        currentMode = 'upload';
        modeUploadBtn.classList.add('btn-primary');
        modeUploadBtn.classList.remove('btn-outline');
        modeUploadBtn.style.color = '';
        modeUploadBtn.style.borderColor = '';

        modeCameraBtn.classList.add('btn-outline');
        modeCameraBtn.classList.remove('btn-primary');
        modeCameraBtn.style.color = 'var(--text-main)';
        modeCameraBtn.style.borderColor = 'var(--glass-border)';

        cameraSection.classList.add('hidden');
        if (!currentFile) {
            uploadContent.classList.remove('hidden');
        }
        stopCamera();
    });

    modeCameraBtn?.addEventListener('click', () => {
        currentMode = 'camera';
        modeCameraBtn.classList.add('btn-primary');
        modeCameraBtn.classList.remove('btn-outline');
        modeCameraBtn.style.color = '';
        modeCameraBtn.style.borderColor = '';

        modeUploadBtn.classList.add('btn-outline');
        modeUploadBtn.classList.remove('btn-primary');
        modeUploadBtn.style.color = 'var(--text-main)';
        modeUploadBtn.style.borderColor = 'var(--glass-border)';

        uploadContent.classList.add('hidden');
        previewContainer.classList.add('hidden');
        resultSection.classList.add('hidden');
        
        currentFile = null;
        fileInput.value = '';
        previewImg.src = '';
        
        cameraSection.classList.remove('hidden');
        startCamera();
    });

    captureBtn?.addEventListener('click', () => {
        if (!stream) return;
        
        const context = cameraCanvas.getContext('2d');
        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        
        context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        cameraCanvas.toBlob((blob) => {
            if (blob) {
                const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                handleFiles([file]);
                stopCamera();
                cameraSection.classList.add('hidden');
            }
        }, 'image/jpeg', 0.9);
    });

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
        previewContainer.classList.add('hidden');
        resultSection.classList.add('hidden');
        
        if (currentMode === 'camera') {
            cameraSection.classList.remove('hidden');
            startCamera();
        } else {
            uploadContent.classList.remove('hidden');
        }
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
                showError(
                    data.message || 'Lỗi từ Backend Server!',
                    data.suggestion || null
                );
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

        // Ingredients
        const ingredientsList = document.getElementById('ingredients-list');
        const ingredientsAccordion = document.getElementById('ingredients-accordion');
        ingredientsList.innerHTML = '';

        if (data.food_data.ingredients && data.food_data.ingredients.length > 0) {
            ingredientsAccordion.style.display = 'block';
            data.food_data.ingredients.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.TenNguyenLieu} — ${item.SoLuong}`;
                ingredientsList.appendChild(li);
            });
        } else {
            ingredientsAccordion.style.display = 'none';
        }

        // Recipe
        const recipeInstructions = document.getElementById('recipe-instructions');
        const recipeTime = document.getElementById('recipe-time');
        const recipeAccordion = document.getElementById('recipe-accordion');

        if (data.food_data.recipe_instructions) {
            recipeAccordion.style.display = 'block';
            recipeInstructions.textContent = data.food_data.recipe_instructions;
            
            if (data.food_data.recipe_time) {
                recipeTime.textContent = `⏱ ${data.food_data.recipe_time} phút`;
            } else {
                recipeTime.textContent = '';
            }
        } else {
            recipeAccordion.style.display = 'none';
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
        
        // Hide recipe and ingredients accordions
        document.getElementById('ingredients-accordion').style.display = 'none';
        document.getElementById('recipe-accordion').style.display = 'none';
    }

    // Health Recommendation Rendering
    const recBox = document.getElementById('health-recommendation-box');
    if (data.health_recommendation && recBox) {
        document.getElementById('rec-bmi').textContent = data.health_recommendation.bmi;
        document.getElementById('rec-bmi-cat').textContent = data.health_recommendation.bmi_category;
        const statusSpan = document.getElementById('rec-status');
        statusSpan.textContent = data.health_recommendation.recommendation;
        document.getElementById('rec-reason').textContent = data.health_recommendation.reason;
        
        // Color coding for status
        statusSpan.style.color = "var(--text-main)";
        if (data.health_recommendation.recommendation.includes("Hạn chế")) {
            statusSpan.style.color = "var(--c-fat)";
            statusSpan.style.background = "rgba(239, 68, 68, 0.1)";
        } else if (data.health_recommendation.recommendation.includes("Nên ăn")) {
            statusSpan.style.color = "var(--c-carb)";
            statusSpan.style.background = "rgba(34, 197, 94, 0.1)";
        } else {
            statusSpan.style.color = "var(--primary)";
            statusSpan.style.background = "rgba(249, 115, 22, 0.1)";
        }
        
        recBox.style.display = 'block';
    } else if (recBox) {
        recBox.style.display = 'none';
    }

    // Initialize accordion functionality
    initAccordion();

    // Scroll result into view
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function initAccordion() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        // Remove old listeners by cloning
        const newHeader = header.cloneNode(true);
        header.parentNode.replaceChild(newHeader, header);
        
        newHeader.addEventListener('click', function() {
            const accordionItem = this.parentElement;
            const isActive = accordionItem.classList.contains('active');
            
            // Close all accordions
            document.querySelectorAll('.accordion-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Open clicked accordion if it wasn't active
            if (!isActive) {
                accordionItem.classList.add('active');
            }
        });
    });
}


function showError(message, suggestion = null) {
    const sysMsg = document.getElementById('sys-msg');
    const resultSection = document.getElementById('result-section');

    resultSection.classList.remove('hidden');
    document.getElementById('food-name').textContent = 'Lỗi Phân Tích';
    
    let fullMessage = message;
    if (suggestion) {
        fullMessage += `\n\n💡 ${suggestion}`;
    }
    
    document.getElementById('food-desc').textContent = fullMessage;
    document.getElementById('confidence-score').textContent = '0';

    sysMsg.textContent = fullMessage;
    sysMsg.classList.add('visible');

    ['val-cal', 'val-prot', 'val-carb', 'val-fat'].forEach(id => {
        document.getElementById(id).textContent = '--';
    });
    
    // Hide recipe and ingredients accordions
    document.getElementById('ingredients-accordion').style.display = 'none';
    document.getElementById('recipe-accordion').style.display = 'none';
    
    // Initialize accordion (for nutrition section)
    initAccordion();
}

function togglePassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        iconElement.classList.remove("fa-eye-slash");
        iconElement.classList.add("fa-eye");
    } else {
        input.type = "password";
        iconElement.classList.remove("fa-eye");
        iconElement.classList.add("fa-eye-slash");
    }
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
        
        const payload = { 
            name, 
            email, 
            password,
            hp_age: document.getElementById('reg-age')?.value,
            hp_height: document.getElementById('reg-height')?.value,
            hp_weight: document.getElementById('reg-weight')?.value,
            hp_gender: document.getElementById('reg-gender')?.value,
            hp_goal: document.getElementById('reg-goal')?.value
        };
        
        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
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

    // Load Health Profile
    try {
        const hpRes = await fetch('/api/health-profile/' + loggedUser.id);
        const hpData = await hpRes.json();
        if (hpData.success && hpData.profile) {
            document.getElementById('hp-age').value = hpData.profile.Tuoi || '';
            document.getElementById('hp-gender').value = hpData.profile.GioiTinh || 'Nam';
            document.getElementById('hp-height').value = hpData.profile.ChieuCao || '';
            document.getElementById('hp-weight').value = hpData.profile.CanNang || '';
            document.getElementById('hp-goal').value = hpData.profile.MucTieu || 'giu_dang';
        }
    } catch (e) {
        console.error("Lỗi tải hồ sơ sức khỏe", e);
    }

    // Health Profile Form Handler
    const hpForm = document.getElementById('health-profile-form');
    if (hpForm && !hpForm.dataset.initialized) {
        hpForm.dataset.initialized = 'true';
        hpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgDiv = document.getElementById('hp-message');
            msgDiv.classList.add('hidden');
            
            const payload = {
                Tuoi: document.getElementById('hp-age').value,
                GioiTinh: document.getElementById('hp-gender').value,
                ChieuCao: document.getElementById('hp-height').value,
                CanNang: document.getElementById('hp-weight').value,
                MucTieu: document.getElementById('hp-goal').value
            };
            
            try {
                const res = await fetch('/api/health-profile/' + loggedUser.id, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const responseData = await res.json();
                
                msgDiv.textContent = responseData.message;
                msgDiv.classList.remove('hidden');
                if (responseData.success) {
                    msgDiv.classList.add('success');
                } else {
                    msgDiv.classList.remove('success');
                }
                setTimeout(() => msgDiv.classList.add('hidden'), 3000);
            } catch (err) {
                msgDiv.textContent = 'Lỗi kết nối';
                msgDiv.classList.remove('hidden', 'success');
            }
        });
    }

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



// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    checkLoginState();
    initAnalyzePage();
    initRevealAnimations();
    initFoodSlider(); // Initialize food banner slider
});



