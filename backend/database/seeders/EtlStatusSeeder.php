<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\EtlStatus;
use Illuminate\Database\Seeder;

class EtlStatusSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $statuses = ['pending', 'downloading', 'downloaded', 'failed', 'parsed'];

        foreach ($statuses as $name) {
            EtlStatus::updateOrInsert(['name' => $name]);
        }
    }
}
