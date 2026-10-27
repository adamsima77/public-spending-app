<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreNutCodeRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'code' => ['required', 'string', 'between:2,5', 'unique:nut_codes,code'],
            'name_sk' => ['required', 'string', 'max:255'],
            'level' => ['required', 'integer', 'between:0,3'],
            'parent_code' => ['nullable', 'string', 'exists:nut_codes,code'],
        ];
    }

    public function messages(): array
    {
        return [
            'code.required' => 'Kód je potrebné vyplniť !.',
            'code.between' => 'Kód musí obsahovať dĺžku 2 až 5 znakov.',
            'code.unique' => 'Tento kód už existuje.',
            'name_sk.required' => 'Názov je povinný.',
            'name_sk.max' => 'Názov môže mať maximálne 255 znakov.',
            'level.required' => 'Úroveň je povinná.',
            'level.integer' => 'Úroveň musí byť celé číslo.',
            'level.between' => 'Úroveň musí byť medzi 0 a 3.',
            'parent_code.exists' => 'Zadaný nadradený kód neexistuje.',
        ];
    }
}
