<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class SystemLogIndexRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'type' => ['nullable', 'string', 'max:32'],
            'event' => ['nullable', 'string', 'max:64'],
            'method' => ['nullable', 'string', 'max:16'],
            'user_id' => ['nullable', 'integer', 'exists:users,id'],
            'created_from' => ['nullable', 'date'],
            'created_to' => ['nullable', 'date', 'after_or_equal:created_from'],
            'per_page' => ['nullable', 'integer', 'between:1,100'],
        ];
    }
}
