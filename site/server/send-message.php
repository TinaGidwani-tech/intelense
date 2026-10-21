<?php
// Receives the website contact form (JSON) and emails it to enquiries@intelense.ca using the server's own mail.
// Upload next to index.html (public_html). The site's JavaScript posts to /send-message.php.

const TO_ADDRESS   = 'enquiries@intelense.ca';
// A mailbox on the domain this site runs on (create it in cPanel > Email Accounts if needed). Mail sent "from" a domain the
// server does not host often lands in spam; the visitor's address goes in Reply-To instead, so Reply works as expected.
const FROM_ADDRESS = 'website@intelense.com';
const MIN_SECONDS_BETWEEN_MESSAGES = 20; // per visitor IP

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function reply(int $status, array $body): void {
    http_response_code($status);
    echo json_encode($body);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    reply(405, ['ok' => false, 'error' => 'POST only']);
}

$raw = file_get_contents('php://input', false, null, 0, 20000);
$in = json_decode($raw ?: '', true);
if (!is_array($in)) {
    reply(400, ['ok' => false, 'error' => 'Bad request']);
}

// Bots fill the hidden field; pretend it worked.
if (!empty($in['_honey'])) {
    reply(200, ['ok' => true]);
}

// One line, no control characters (stops header injection), trimmed to a sensible length.
function clean(string $v, int $max): string {
    $v = preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $v) ?? '';
    return mb_substr(trim($v), 0, $max);
}
$first    = clean((string)($in['first_name'] ?? ''), 80);
$last     = clean((string)($in['last_name'] ?? ''), 80);
$email    = clean((string)($in['email'] ?? ''), 200);
$company  = clean((string)($in['company'] ?? ''), 150);
$interest = clean((string)($in['interest'] ?? ''), 80);
$message  = mb_substr(trim(str_replace("\r", '', (string)($in['message'] ?? ''))), 0, 5000);

if ($first === '' || $last === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    reply(422, ['ok' => false, 'error' => 'Please fill in your name, a valid email and a message.']);
}

// Simple per-IP throttle.
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$stamp = sys_get_temp_dir() . '/intelense-form-' . md5($ip);
if (is_file($stamp) && time() - (int)@filemtime($stamp) < MIN_SECONDS_BETWEEN_MESSAGES) {
    reply(429, ['ok' => false, 'error' => 'Please wait a moment before sending another message.']);
}

$name = $first . ' ' . $last;
$subject = 'Message from ' . $name . ' via intelense.com';
$body = "New message from the intelense.com contact form\n\n"
      . "Name: $name\nWork email: $email\nCompany: $company\nInterested in: $interest\n\n"
      . "Message:\n$message\n\n--\nSent from IP $ip on " . gmdate('Y-m-d H:i') . " UTC\n";
$headers = [
    'From: Intelense website <' . FROM_ADDRESS . '>',
    'Reply-To: ' . trim(preg_replace('/[<>":;,@]+/', ' ', $name)) . ' <' . $email . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: intelense-contact-form',
];

$sent = mail(TO_ADDRESS, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, implode("\r\n", $headers), '-f' . FROM_ADDRESS);
if (!$sent) {
    error_log('intelense contact form: mail() failed for ' . $email);
    reply(500, ['ok' => false, 'error' => 'We could not send that message.']);
}
@touch($stamp);
reply(200, ['ok' => true]);
