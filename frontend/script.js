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
    navigateTo(hash);
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

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
    initAnalyzePage();
    initRevealAnimations();
});
