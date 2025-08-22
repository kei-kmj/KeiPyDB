# アニメーション例

<div class="moving-icon">🚀</div>

<style>
.moving-icon {
  font-size: 3rem;
  position: absolute;
  top: 50%;
  left: 0;
  animation: moveRight 3s ease-in-out infinite;
}

@keyframes moveRight {
  0% {
    left: 0;
    transform: translateY(-50%);
  }
  50% {
    left: 50%;
    transform: translate(-50%, -50%);
  }
  100% {
    left: calc(100% - 60px);
    transform: translate(-100%, -50%);
  }
}
</style>

<!-- より複雑なアニメーション例 -->
<div class="data-flow">
  <div class="step" style="left: 10%;">📊 データ</div>
  <div class="arrow">→</div>
  <div class="step" style="left: 50%;">⚙️ 処理</div>
  <div class="arrow2">→</div>
  <div class="step" style="left: 80%;">📈 結果</div>
</div>

<style>
.data-flow {
  position: relative;
  height: 100px;
  margin-top: 100px;
}

.step {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.5rem;
  opacity: 0;
  animation: fadeInSlide 1s ease-out forwards;
}

.step:nth-child(1) { animation-delay: 0s; }
.step:nth-child(3) { animation-delay: 1s; }
.step:nth-child(5) { animation-delay: 2s; }

.arrow, .arrow2 {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 2rem;
  opacity: 0;
}

.arrow {
  left: 28%;
  animation: fadeIn 0.5s ease-out 0.5s forwards;
}

.arrow2 {
  left: 68%;
  animation: fadeIn 0.5s ease-out 1.5s forwards;
}

@keyframes fadeInSlide {
  0% {
    opacity: 0;
    transform: translateY(-50%) translateX(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(-50%) translateX(0);
  }
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
</style>