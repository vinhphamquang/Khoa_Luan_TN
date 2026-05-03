// Nutrition Plan JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    
    if (!loggedUser) {
        window.location.href = '/';
        return;
    }

    // --- Navbar Setup ---
    const displayUsername = document.getElementById('display-username');
    if (displayUsername) displayUsername.textContent = loggedUser.name;

    if (loggedUser.role === 'admin') {
        const adminLink = document.getElementById('nav-admin-link');
        if (adminLink) adminLink.style.display = '';
    }

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            localStorage.removeItem('smartfood_user');
            window.location.href = '/';
        });
    }

    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => navLinks.classList.toggle('show'));
    }

    loadHealthProfile();
    loadPlanHistory();

    const form = document.getElementById('health-profile-form');
    form.addEventListener('submit', handleFormSubmit);
});

let currentPlan = null;

// Meal distribution config
const MEAL_CONFIG = {
    breakfast: { percent: 0.25, name: 'Bữa Sáng', emoji: '🌅' },
    lunch:     { percent: 0.35, name: 'Bữa Trưa', emoji: '☀️' },
    dinner:    { percent: 0.30, name: 'Bữa Tối', emoji: '🌙' },
    snack:     { percent: 0.10, name: 'Bữa Phụ', emoji: '🍎' }
};

// Track selected foods per meal
let selectedFoods = {
    breakfast: null,
    lunch: null,
    dinner: null,
    snack: null
};

// Store all available foods per meal for swap suggestions
let mealFoodLists = {
    breakfast: [],
    lunch: [],
    dinner: [],
    snack: []
};

async function loadHealthProfile() {
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    try {
        const response = await fetch(`/api/health-profile/${loggedUser.id}`);
        const data = await response.json();
        if (data.success && data.profile) {
            const profile = data.profile;
            document.getElementById('weight').value = profile.CanNang;
            document.getElementById('height').value = profile.ChieuCao;
            document.getElementById('age').value = profile.Tuoi;
            document.getElementById('gender').value = profile.GioiTinh;
            document.getElementById('activity').value = profile.MucDoVanDong;
            document.getElementById('goal').value = profile.MucTieu;
            if (profile.BMR && profile.TDEE) {
                displayResults(profile);
            }
        }
    } catch (error) {
        console.error('Error loading health profile:', error);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    const data = {
        CanNang: parseFloat(document.getElementById('weight').value),
        ChieuCao: parseFloat(document.getElementById('height').value),
        Tuoi: parseInt(document.getElementById('age').value),
        GioiTinh: document.getElementById('gender').value,
        MucDoVanDong: document.getElementById('activity').value,
        MucTieu: document.getElementById('goal').value
    };
    try {
        const response = await fetch(`/api/health-profile/${loggedUser.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            const profileResponse = await fetch(`/api/health-profile/${loggedUser.id}`);
            const profileData = await profileResponse.json();
            if (profileData.success) {
                // Reset selections when recalculating
                selectedFoods = { breakfast: null, lunch: null, dinner: null, snack: null };
                mealFoodLists = { breakfast: [], lunch: [], dinner: [], snack: [] };
                displayResults(profileData.profile);
            }
        } else {
            alert('Có lỗi xảy ra: ' + result.message);
        }
    } catch (error) {
        console.error('Error saving health profile:', error);
        alert('Lỗi kết nối server');
    }
}

function displayResults(profile) {
    currentPlan = profile;
    
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('hidden');
    
    animateValue('bmr-value', 0, Math.round(profile.BMR), 800);
    animateValue('tdee-value', 0, Math.round(profile.TDEE), 800);
    animateValue('target-value', 0, Math.round(profile.CaloDuKien), 800);
    
    const bmi = profile.CanNang / ((profile.ChieuCao / 100) ** 2);
    animateValue('bmi-value', 0, bmi, 800, 1);
    
    let bmiCategory = '', bmiColor = '';
    if (bmi < 18.5) { bmiCategory = 'Gầy'; bmiColor = '#3b82f6'; }
    else if (bmi < 25) { bmiCategory = 'Bình thường'; bmiColor = '#22c55e'; }
    else if (bmi < 30) { bmiCategory = 'Thừa cân'; bmiColor = '#f59e0b'; }
    else { bmiCategory = 'Béo phì'; bmiColor = '#ef4444'; }
    
    const bmiCategoryEl = document.getElementById('bmi-category');
    bmiCategoryEl.textContent = bmiCategory;
    bmiCategoryEl.style.color = bmiColor;
    bmiCategoryEl.style.fontWeight = '600';
    
    const targetCalo = profile.CaloDuKien;
    for (const [mealType, config] of Object.entries(MEAL_CONFIG)) {
        const mealCalo = Math.round(targetCalo * config.percent);
        const caloEl = document.getElementById(`${mealType}-calo`);
        if (caloEl) caloEl.textContent = `${mealCalo} kcal`;
        const targetEl = document.getElementById(`${mealType}-target`);
        if (targetEl) targetEl.textContent = mealCalo;
    }
    
    loadAllMealSuggestions(targetCalo);
    
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
}

function animateValue(elementId, start, end, duration, decimals = 0) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        el.textContent = (start + (end - start) * easeOut).toFixed(decimals);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

async function loadAllMealSuggestions(totalCalo) {
    const promises = Object.entries(MEAL_CONFIG).map(([mealType, config]) => {
        return loadMealSuggestions(mealType, Math.round(totalCalo * config.percent));
    });
    await Promise.all(promises);
}

async function loadMealSuggestions(mealType, mealCalo) {
    const container = document.getElementById(`${mealType}-suggestions`);
    if (!container) return;
    
    container.innerHTML = '<div class="np-loading"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải đề xuất...</div>';
    
    try {
        const response = await fetch(`/api/meal-suggestions?meal_type=${mealType}&target_calo=${mealCalo}`);
        const data = await response.json();
        
        if (data.success && data.suggestions && data.suggestions.length > 0) {
            mealFoodLists[mealType] = data.suggestions;
            renderFoodCards(container, data.suggestions, mealCalo, mealType);
        } else {
            container.innerHTML = `<div class="np-no-data"><i class="fa-solid fa-bowl-food"></i><p>Chưa có đề xuất phù hợp</p></div>`;
        }
    } catch (error) {
        console.error(`Error loading ${mealType}:`, error);
        container.innerHTML = `<div class="np-no-data"><i class="fa-solid fa-exclamation-triangle"></i><p>Lỗi khi tải đề xuất</p></div>`;
    }
}

function renderFoodCards(container, suggestions, targetCalo, mealType) {
    // Find the best match (closest to target calo)
    let bestIndex = 0;
    let bestDiff = Infinity;
    suggestions.forEach((food, i) => {
        const diff = Math.abs(food.calories - targetCalo);
        if (diff < bestDiff) {
            bestDiff = diff;
            bestIndex = i;
        }
    });
    
    // Auto-select the best match
    selectedFoods[mealType] = suggestions[bestIndex];
    const bestFood = suggestions[bestIndex];
    const otherFoods = suggestions.filter((_, i) => i !== bestIndex);
    
    // Build main recommended card (always visible)
    let html = `
        <div class="np-food-card selected recommended good-match" 
             data-meal="${mealType}" data-food-id="${bestFood.id}"
             onclick="selectFood('${mealType}', ${JSON.stringify(bestFood).replace(/"/g, '&quot;')})"
             style="animation: pageFadeIn 0.4s ease both; cursor: pointer;">
            <div class="np-recommended-badge"><i class="fa-solid fa-star"></i> Đề xuất tốt nhất</div>
            <div class="np-food-header">
                <div class="np-food-name">${bestFood.name}</div>
                <div class="np-food-calo-badge">${bestFood.calories} kcal</div>
            </div>
            <div class="np-food-category"><i class="fa-solid fa-tag"></i> ${bestFood.category}</div>
            ${bestFood.description ? `<p class="np-food-desc">${bestFood.description}</p>` : ''}
            <div class="np-food-nutrition">
                <div class="np-nutrition-item">
                    <div class="np-nutrition-label">Protein</div>
                    <div class="np-nutrition-value" style="color: var(--c-prot);">${bestFood.protein}g</div>
                </div>
                <div class="np-nutrition-item">
                    <div class="np-nutrition-label">Carbs</div>
                    <div class="np-nutrition-value" style="color: var(--c-carb);">${bestFood.carbs}g</div>
                </div>
                <div class="np-nutrition-item">
                    <div class="np-nutrition-label">Chất béo</div>
                    <div class="np-nutrition-value" style="color: var(--c-fat);">${bestFood.fats}g</div>
                </div>
            </div>
            <div class="np-select-indicator">
                <i class="fa-solid fa-check-circle"></i>
                <span>Đã chọn</span>
            </div>
        </div>
    `;
    
    // "Xem thêm" button + collapsible list
    if (otherFoods.length > 0) {
        html += `
            <div class="np-more-section">
                <button class="np-more-btn" onclick="toggleMoreFoods('${mealType}', this)">
                    <i class="fa-solid fa-chevron-down"></i>
                    <span>Xem thêm ${otherFoods.length} món khác</span>
                </button>
                <div class="np-more-list" id="more-${mealType}" style="display:none;">
        `;
        otherFoods.forEach((food, index) => {
            const isSelected = selectedFoods[mealType] && selectedFoods[mealType].id === food.id;
            const caloriesDiff = Math.abs(food.calories - targetCalo);
            const isGoodMatch = caloriesDiff <= targetCalo * 0.2;
            
            html += `
                <div class="np-food-card ${isSelected ? 'selected' : ''} ${isGoodMatch ? 'good-match' : ''}" 
                     data-meal="${mealType}" data-food-id="${food.id}"
                     onclick="selectFood('${mealType}', ${JSON.stringify(food).replace(/"/g, '&quot;')})"
                     style="animation: pageFadeIn 0.3s ${index * 0.04}s ease both; cursor: pointer;">
                    <div class="np-food-header">
                        <div class="np-food-name">${food.name}</div>
                        <div class="np-food-calo-badge">${food.calories} kcal</div>
                    </div>
                    <div class="np-food-category"><i class="fa-solid fa-tag"></i> ${food.category}</div>
                    ${food.description ? `<p class="np-food-desc">${food.description}</p>` : ''}
                    <div class="np-food-nutrition">
                        <div class="np-nutrition-item">
                            <div class="np-nutrition-label">Protein</div>
                            <div class="np-nutrition-value" style="color: var(--c-prot);">${food.protein}g</div>
                        </div>
                        <div class="np-nutrition-item">
                            <div class="np-nutrition-label">Carbs</div>
                            <div class="np-nutrition-value" style="color: var(--c-carb);">${food.carbs}g</div>
                        </div>
                        <div class="np-nutrition-item">
                            <div class="np-nutrition-label">Chất béo</div>
                            <div class="np-nutrition-value" style="color: var(--c-fat);">${food.fats}g</div>
                        </div>
                    </div>
                    <div class="np-select-indicator">
                        <i class="fa-solid ${isSelected ? 'fa-check-circle' : 'fa-circle-plus'}"></i>
                        <span>${isSelected ? 'Đã chọn' : 'Nhấn để chọn'}</span>
                    </div>
                </div>
            `;
        });
        html += `</div></div>`;
    }
    
    container.innerHTML = html;
    
    // Update daily summary after rendering
    updateDailySummary();
}

// Toggle "Xem thêm" section
window.toggleMoreFoods = function(mealType, btn) {
    const list = document.getElementById(`more-${mealType}`);
    const icon = btn.querySelector('i');
    const text = btn.querySelector('span');
    const isHidden = list.style.display === 'none';
    
    list.style.display = isHidden ? 'grid' : 'none';
    icon.className = isHidden ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down';
    text.textContent = isHidden 
        ? 'Ẩn bớt' 
        : `Xem thêm ${list.querySelectorAll('.np-food-card').length} món khác`;
    btn.classList.toggle('expanded', isHidden);
};

// Global function for selecting a food from a meal
window.selectFood = function(mealType, food) {
    // Toggle: if same food clicked, deselect
    if (selectedFoods[mealType] && selectedFoods[mealType].id === food.id) {
        selectedFoods[mealType] = null;
    } else {
        selectedFoods[mealType] = food;
    }
    
    // Update card selection visuals
    const container = document.getElementById(`${mealType}-suggestions`);
    const cards = container.querySelectorAll('.np-food-card');
    cards.forEach(card => {
        const cardId = parseInt(card.dataset.foodId);
        const isSelected = selectedFoods[mealType] && selectedFoods[mealType].id === cardId;
        card.classList.toggle('selected', isSelected);
        
        const indicator = card.querySelector('.np-select-indicator');
        if (indicator) {
            indicator.innerHTML = isSelected
                ? '<i class="fa-solid fa-check-circle"></i><span>Đã chọn</span>'
                : '<i class="fa-solid fa-circle-plus"></i><span>Nhấn để chọn</span>';
        }
    });
    
    updateDailySummary();
};

function updateDailySummary() {
    const summarySection = document.getElementById('daily-summary');
    const summaryContent = document.getElementById('summary-content');
    const summaryTotal = document.getElementById('summary-total');
    
    const hasAnySelection = Object.values(selectedFoods).some(f => f !== null);
    
    if (!hasAnySelection) {
        summarySection.classList.add('hidden');
        return;
    }
    
    summarySection.classList.remove('hidden');
    
    let totalCalo = 0, totalProtein = 0, totalCarbs = 0, totalFats = 0;
    let contentHtml = '<div class="np-summary-meals">';
    
    for (const [mealType, config] of Object.entries(MEAL_CONFIG)) {
        const food = selectedFoods[mealType];
        const mealCalo = currentPlan ? Math.round(currentPlan.CaloDuKien * config.percent) : 0;
        
        contentHtml += `
            <div class="np-summary-meal-row ${food ? 'has-food' : 'empty'}">
                <div class="np-summary-meal-label">
                    <span class="np-summary-emoji">${config.emoji}</span>
                    <span class="np-summary-meal-name">${config.name}</span>
                    <span class="np-summary-meal-target">(${mealCalo} kcal)</span>
                </div>
                <div class="np-summary-meal-food">
        `;
        
        if (food) {
            totalCalo += food.calories;
            totalProtein += food.protein;
            totalCarbs += food.carbs;
            totalFats += food.fats;
            
            const diff = food.calories - mealCalo;
            const diffClass = Math.abs(diff) <= mealCalo * 0.2 ? 'good' : (diff > 0 ? 'over' : 'under');
            const diffText = diff > 0 ? `+${diff}` : `${diff}`;
            
            contentHtml += `
                <span class="np-summary-food-name">${food.name}</span>
                <span class="np-summary-food-calo">${food.calories} kcal</span>
                <span class="np-summary-diff ${diffClass}">${diffText}</span>
            `;
        } else {
            contentHtml += '<span class="np-summary-empty">Chưa chọn món</span>';
        }
        
        contentHtml += '</div></div>';
    }
    
    contentHtml += '</div>';
    summaryContent.innerHTML = contentHtml;
    
    // Total summary
    const targetTotal = currentPlan ? Math.round(currentPlan.CaloDuKien) : 0;
    const totalDiff = totalCalo - targetTotal;
    const totalDiffClass = Math.abs(totalDiff) <= targetTotal * 0.1 ? 'good' : (totalDiff > 0 ? 'over' : 'under');
    const totalDiffText = totalDiff > 0 ? `+${totalDiff}` : `${totalDiff}`;
    const progressPercent = targetTotal > 0 ? Math.min((totalCalo / targetTotal) * 100, 120) : 0;
    
    summaryTotal.innerHTML = `
        <div class="np-summary-progress-bar">
            <div class="np-summary-progress-fill ${totalDiffClass}" style="width: ${progressPercent}%"></div>
        </div>
        <div class="np-summary-total-row">
            <div class="np-summary-total-label">
                <i class="fa-solid fa-fire-flame-curved"></i> Tổng calo ngày
            </div>
            <div class="np-summary-total-values">
                <span class="np-summary-total-number">${totalCalo}</span>
                <span class="np-summary-total-separator">/</span>
                <span class="np-summary-total-target">${targetTotal} kcal</span>
                <span class="np-summary-total-diff ${totalDiffClass}">(${totalDiffText})</span>
            </div>
        </div>
        <div class="np-summary-macros">
            <div class="np-summary-macro">
                <span class="np-summary-macro-label">Protein</span>
                <span class="np-summary-macro-value" style="color: var(--c-prot);">${totalProtein.toFixed(1)}g</span>
            </div>
            <div class="np-summary-macro">
                <span class="np-summary-macro-label">Carbs</span>
                <span class="np-summary-macro-value" style="color: var(--c-carb);">${totalCarbs.toFixed(1)}g</span>
            </div>
            <div class="np-summary-macro">
                <span class="np-summary-macro-label">Chất béo</span>
                <span class="np-summary-macro-value" style="color: var(--c-fat);">${totalFats.toFixed(1)}g</span>
            </div>
        </div>
    `;

    // Generate adjustment suggestions if total is off
    const adjustHtml = generateAdjustmentSuggestion(totalCalo, targetTotal);
    if (adjustHtml) {
        summaryTotal.innerHTML += adjustHtml;
    }
}

function generateAdjustmentSuggestion(totalCalo, targetTotal) {
    const diff = totalCalo - targetTotal;
    const threshold = targetTotal * 0.1; // 10% tolerance
    
    if (Math.abs(diff) <= threshold) {
        // Within acceptable range
        return `
            <div class="np-adjust-box good">
                <div class="np-adjust-icon"><i class="fa-solid fa-circle-check"></i></div>
                <div class="np-adjust-content">
                    <div class="np-adjust-title">Thực đơn phù hợp!</div>
                    <div class="np-adjust-desc">Tổng calo đã chọn nằm trong khoảng cho phép (±10%) so với mục tiêu ${targetTotal} kcal/ngày.</div>
                </div>
            </div>
        `;
    }
    
    const needReduce = diff > 0;
    const absDiff = Math.abs(diff);
    
    // Find the best swap across all meals
    let bestSwap = null;
    
    for (const [mealType, config] of Object.entries(MEAL_CONFIG)) {
        const currentFood = selectedFoods[mealType];
        if (!currentFood) continue;
        
        const alternatives = mealFoodLists[mealType];
        if (!alternatives || alternatives.length < 2) continue;
        
        for (const alt of alternatives) {
            if (alt.id === currentFood.id) continue;
            
            const calChange = alt.calories - currentFood.calories;
            
            // If we need to reduce, find food with fewer calories (negative calChange)
            // If we need to increase, find food with more calories (positive calChange)
            if (needReduce && calChange >= 0) continue;
            if (!needReduce && calChange <= 0) continue;
            
            // Calculate how well this swap fixes the problem
            const newTotal = totalCalo + calChange;
            const newDiff = Math.abs(newTotal - targetTotal);
            
            if (!bestSwap || newDiff < bestSwap.newDiff) {
                bestSwap = {
                    mealType,
                    mealName: config.name,
                    mealEmoji: config.emoji,
                    currentFood: currentFood,
                    newFood: alt,
                    calChange,
                    newTotal,
                    newDiff
                };
            }
        }
    }
    
    if (!bestSwap) {
        return `
            <div class="np-adjust-box ${needReduce ? 'over' : 'under'}">
                <div class="np-adjust-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
                <div class="np-adjust-content">
                    <div class="np-adjust-title">${needReduce ? 'Vượt' : 'Thiếu'} ${absDiff} kcal so với mục tiêu</div>
                    <div class="np-adjust-desc">Hãy thử chọn các món ${needReduce ? 'ít' : 'nhiều'} calo hơn ở các bữa để cân chỉnh.</div>
                </div>
            </div>
        `;
    }
    
    const changeText = bestSwap.calChange > 0 ? `+${bestSwap.calChange}` : `${bestSwap.calChange}`;
    const actionText = needReduce ? 'giảm' : 'tăng';
    
    return `
        <div class="np-adjust-box ${needReduce ? 'over' : 'under'}">
            <div class="np-adjust-icon"><i class="fa-solid fa-lightbulb"></i></div>
            <div class="np-adjust-content">
                <div class="np-adjust-title">
                    ${needReduce ? 'Vượt' : 'Thiếu'} <strong>${absDiff} kcal</strong> — Gợi ý điều chỉnh:
                </div>
                <div class="np-adjust-suggestion" 
                     onclick="applySwap('${bestSwap.mealType}', ${JSON.stringify(bestSwap.newFood).replace(/"/g, '&quot;')})">
                    <div class="np-swap-detail">
                        <span class="np-swap-emoji">${bestSwap.mealEmoji}</span>
                        <span class="np-swap-meal">${bestSwap.mealName}:</span>
                        <span class="np-swap-from">${bestSwap.currentFood.name} (${bestSwap.currentFood.calories} kcal)</span>
                        <i class="fa-solid fa-arrow-right"></i>
                        <span class="np-swap-to">${bestSwap.newFood.name} (${bestSwap.newFood.calories} kcal)</span>
                        <span class="np-swap-change ${needReduce ? 'reduce' : 'increase'}">${changeText} kcal</span>
                    </div>
                    <button class="np-swap-btn">
                        <i class="fa-solid fa-arrows-rotate"></i> Áp dụng
                    </button>
                </div>
            </div>
        </div>
    `;
}

window.applySwap = function(mealType, newFood) {
    selectFood(mealType, newFood);
    
    // Scroll to the summary
    setTimeout(() => {
        document.getElementById('daily-summary').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300);
};

// ============================================
// SAVE & HISTORY
// ============================================

window.saveMealPlan = async function() {
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    if (!loggedUser || !currentPlan) return;
    
    const hasAny = Object.values(selectedFoods).some(f => f !== null);
    if (!hasAny) {
        alert('Hãy chọn ít nhất một món ăn trước khi lưu!');
        return;
    }
    
    const btn = document.getElementById('btn-save-plan');
    const status = document.getElementById('save-status');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';
    
    let totalCalo = 0;
    for (const food of Object.values(selectedFoods)) {
        if (food) totalCalo += food.calories;
    }
    
    const payload = {
        caloDuKien: currentPlan.CaloDuKien,
        tongCaloChon: totalCalo,
        buaSang: selectedFoods.breakfast?.name || '',
        buaSangCalo: selectedFoods.breakfast?.calories || 0,
        buaTrua: selectedFoods.lunch?.name || '',
        buaTruaCalo: selectedFoods.lunch?.calories || 0,
        buaToi: selectedFoods.dinner?.name || '',
        buaToiCalo: selectedFoods.dinner?.calories || 0,
        buaPhu: selectedFoods.snack?.name || '',
        buaPhuCalo: selectedFoods.snack?.calories || 0
    };
    
    try {
        const res = await fetch(`/api/meal-plans/${loggedUser.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.success) {
            status.innerHTML = '<i class="fa-solid fa-check-circle" style="color: #16a34a;"></i> Đã lưu thành công!';
            status.className = 'np-save-status show success';
            loadPlanHistory();
        } else {
            status.innerHTML = '<i class="fa-solid fa-xmark-circle" style="color: #ef4444;"></i> Lỗi: ' + data.message;
            status.className = 'np-save-status show error';
        }
    } catch (err) {
        status.innerHTML = '<i class="fa-solid fa-xmark-circle" style="color: #ef4444;"></i> Lỗi kết nối';
        status.className = 'np-save-status show error';
    }
    
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Lưu Kế Hoạch Hôm Nay';
    
    setTimeout(() => { status.className = 'np-save-status'; }, 4000);
};

async function loadPlanHistory() {
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    if (!loggedUser) return;
    
    const container = document.getElementById('plan-history-content');
    
    try {
        const res = await fetch(`/api/meal-plans/${loggedUser.id}`);
        const data = await res.json();
        
        if (data.success && data.plans.length > 0) {
            renderPlanHistory(container, data.plans);
        } else {
            container.innerHTML = `
                <div class="np-no-data">
                    <i class="fa-solid fa-calendar-xmark"></i>
                    <p>Chưa có kế hoạch nào được lưu</p>
                </div>
            `;
        }
    } catch (err) {
        console.error('Error loading plan history:', err);
        container.innerHTML = `<div class="np-no-data"><i class="fa-solid fa-exclamation-triangle"></i><p>Lỗi tải lịch sử</p></div>`;
    }
}

function renderPlanHistory(container, plans) {
    // Group by month
    const months = {};
    plans.forEach(plan => {
        const key = plan.month;
        if (!months[key]) months[key] = [];
        months[key].push(plan);
    });
    
    let html = '';
    for (const [month, monthPlans] of Object.entries(months)) {
        const [year, mon] = month.split('-');
        const monthName = `Tháng ${parseInt(mon)}/${year}`;
        
        // Monthly stats
        const avgTarget = monthPlans.reduce((s, p) => s + p.caloDuKien, 0) / monthPlans.length;
        const avgActual = monthPlans.reduce((s, p) => s + p.tongCaloChon, 0) / monthPlans.length;
        const totalDays = monthPlans.length;
        const goodDays = monthPlans.filter(p => Math.abs(p.tongCaloChon - p.caloDuKien) <= p.caloDuKien * 0.1).length;
        
        html += `
            <div class="np-month-group">
                <div class="np-month-header">
                    <div class="np-month-title">
                        <i class="fa-solid fa-calendar"></i>
                        <span>${monthName}</span>
                        <span class="np-month-count">${totalDays} ngày</span>
                    </div>
                    <div class="np-month-stats">
                        <div class="np-month-stat">
                            <span class="np-month-stat-label">TB Mục tiêu</span>
                            <span class="np-month-stat-value">${Math.round(avgTarget)} kcal</span>
                        </div>
                        <div class="np-month-stat">
                            <span class="np-month-stat-label">TB Thực tế</span>
                            <span class="np-month-stat-value">${Math.round(avgActual)} kcal</span>
                        </div>
                        <div class="np-month-stat">
                            <span class="np-month-stat-label">Đạt mục tiêu</span>
                            <span class="np-month-stat-value good">${goodDays}/${totalDays}</span>
                        </div>
                    </div>
                </div>
                <div class="np-month-plans">
        `;
        
        monthPlans.forEach(plan => {
            const diff = plan.tongCaloChon - plan.caloDuKien;
            const statusClass = Math.abs(diff) <= plan.caloDuKien * 0.1 ? 'good' : (diff > 0 ? 'over' : 'under');
            const diffText = diff > 0 ? `+${Math.round(diff)}` : `${Math.round(diff)}`;
            const date = plan.date.split(' ')[0]; // Just the date part
            const time = plan.date.split(' ')[1] || '';
            
            html += `
                <div class="np-plan-card">
                    <div class="np-plan-date">
                        <span class="np-plan-day">${date}</span>
                        <span class="np-plan-time">${time}</span>
                    </div>
                    <div class="np-plan-meals">
                        <div class="np-plan-meal"><span class="np-plan-meal-emoji">🌅</span> ${plan.buaSang || '—'} <span class="np-plan-meal-calo">${plan.buaSangCalo} kcal</span></div>
                        <div class="np-plan-meal"><span class="np-plan-meal-emoji">☀️</span> ${plan.buaTrua || '—'} <span class="np-plan-meal-calo">${plan.buaTruaCalo} kcal</span></div>
                        <div class="np-plan-meal"><span class="np-plan-meal-emoji">🌙</span> ${plan.buaToi || '—'} <span class="np-plan-meal-calo">${plan.buaToiCalo} kcal</span></div>
                        <div class="np-plan-meal"><span class="np-plan-meal-emoji">🍎</span> ${plan.buaPhu || '—'} <span class="np-plan-meal-calo">${plan.buaPhuCalo} kcal</span></div>
                    </div>
                    <div class="np-plan-total">
                        <span class="np-plan-total-number">${Math.round(plan.tongCaloChon)}</span>
                        <span class="np-plan-total-sep">/</span>
                        <span class="np-plan-total-target">${Math.round(plan.caloDuKien)}</span>
                        <span class="np-plan-diff ${statusClass}">${diffText}</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    container.innerHTML = html;
}
