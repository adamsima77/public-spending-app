<?php

declare(strict_types=1);

namespace App\Services;

use App\Enums\ContactEnum;
use App\Models\ContactMessage;

class ContactMessageService
{
    public function createContactMessage(array $data): void
    {
        ContactMessage::create([
            'name' => $data['name'],
            'surname' => $data['surname'],
            'email' => $data['email'],
            'message' => $data['message'],
            'status' => ContactEnum::RECEIVED->value,
        ]);
    }
}
