let timer;
let secondsLeft = 60;

function startTimer() {
  timer = setInterval(updateTimer, 1000);
}

function updateTimer() {
  const minutes = Math.floor(secondsLeft / 60);
  let seconds = secondsLeft % 60;
  seconds = seconds < 10 ? '0' + seconds : seconds;
  document.getElementById('timer').innerText = `${minutes}:${seconds}`;
  secondsLeft--;
  if (secondsLeft < 0) {
    clearInterval(timer);
    document.getElementById('timer').innerText = 'Time\'s up!';
  }
}

function moveToNext(currentInput, nextInputId) {
  const maxLength = parseInt(currentInput.getAttribute('maxlength'));
  const currentLength = currentInput.value.length;
  if (currentLength >= maxLength) {
    if (nextInputId) {
      const nextInput = document.getElementById(nextInputId);
      nextInput.focus();
    }
  }
}

function resendOTP() {
  clearInterval(timer);
  alert("OTP Resent!")
  secondsLeft = 60;
  startTimer();
}

startTimer();
