<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Rules\Password;

class UpdateUserRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'email' => ['sometimes', 'required', 'string', 'email', 'max:255', Rule::unique('users')->ignore($user->id)],
            'password' => ['sometimes', 'required', 'string', Password::min(8)->letters()->mixedCase()->numbers()->symbols()],
            'name' => ['sometimes', 'required', 'string', 'max:255'], 
            'surname' => ['sometimes', 'required', 'string', 'max:255']
        ];
    }

    public function messages(): array
    {
        return [
            'email.required' => 'Email je povinný.',
            'email.string' => 'Email musí byť reťazec.',
            'email.email' => 'Email nemá platný formát.',
            'email.max' => 'Email môže mať maximálne 255 znakov.',
            'email.unique' => 'Email musí byť unikátny.',
            'password.required' => 'Heslo je povinné.',
            'password.string' => 'Heslo musí byť reťazec.',
            'password.min' => 'Heslo musí obsahovať aspoň 8 znakov.',
            'password.letters' => 'Heslo musí mať aspoň jedno písmeno.',
            'password.mixed' => 'Heslo musí obsahovať malé aj veľké písmená.',
            'password.numbers' => 'Heslo musí obsahovať aspoň jedno číslo.',
            'password.symbols' => 'Heslo musí obsahovať aspoň jeden špeciálny znak.',
            'name.required' => 'Meno je povinné.',
            'name.string' => 'Meno musí byť reťazec.',
            'name.max' => 'Meno môže mať maximálne 255 znakov.',
            'surname.required' => 'Priezvisko je povinné.',
            'surname.string' => 'Priezvisko musí byť reťazec.',
            'surname.max' => 'Priezvisko môže mať maximálne 255 znakov.',
        ];
}
}
