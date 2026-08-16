<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\EtlStatus;

class EtlStatusSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $etlStatuses = [
            ['code' => 'pending',    'name' => 'Čaká na stiahnutie', 'created_at' => now(), 'updated_at' => now()],
            ['code' => 'downloaded', 'name' => 'Stiahnuté',          'created_at' => now(), 'updated_at' => now()],
            ['code' => 'processing', 'name' => 'Spracováva sa',      'created_at' => now(), 'updated_at' => now()],
            ['code' => 'parsed',     'name' => 'Spracované',         'created_at' => now(), 'updated_at' => now()],
            ['code' => 'failed',     'name' => 'Chyba',              'created_at' => now(), 'updated_at' => now()],
        ];
        
        EtlStatus::upsert($etlStatuses, ['code'], ['name', 'updated_at']);
    }
}