<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Str;

class UserService
{
    /** @return LengthAwarePaginator<int, User> */
    public function getAllUsers(): LengthAwarePaginator
    {
        return User::with(['role'])->paginate(15);
    }

    /** @param array<string, mixed> $validatedData */
    public function updateUser(User $user, array $validatedData): void
    {
        $user->update([
            'name' => $validatedData['name'],
            'surname' => $validatedData['surname'],
            'email' => $validatedData['email'],
            'password' => $validatedData['password'],
        ]);
    }

    public function anonymizeUser(User $user): void
    {
        $user->forceFill([
            'name' => 'Anonymized',
            'surname' => 'User',
            'email' => 'anonymized' . $user->id . '@anonymized.anon',
            'email_verified_at' => null,
            'password' => bcrypt(Str::random(40)),
        ])->save();
    }
}
