<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class NoticeIndexRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'search' => ['nullable', 'string', 'max:255'],
            'notice_type' => ['nullable', 'string', 'max:32'],
            'form_type' => ['nullable', 'string', 'max:32'],
            'procedure_id' => ['nullable', 'integer', 'exists:procedures,id'],
            'is_latest' => ['nullable', 'boolean'],
            'published_from' => ['nullable', 'date'],
            'published_to' => ['nullable', 'date', 'after_or_equal:published_from'],
            'per_page' => ['nullable', 'integer', 'between:1,100'],
            'page' => ['nullable', 'integer', 'min:1'],
        ];
    }
}
