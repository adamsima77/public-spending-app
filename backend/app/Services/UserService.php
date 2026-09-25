<?php

namespace App\Services;
use App\Models\User;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Str;

class UserService {

    public function getAllUsers(): LengthAwarePaginator
    {
        return User::with(['role'])->paginate(15);
    }    

    public function updateUser(User $user, array $validateEntryData): void
    {
        $user->update([
            'name' => $validateEntryData['name'],
            'surname' => $validateEntryData['surname'],
            'email' => $validateEntryData['email'],
            'password' => $validateEntryData['password'],
        ]);
    }

    public function anonymizeUser($user): void
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