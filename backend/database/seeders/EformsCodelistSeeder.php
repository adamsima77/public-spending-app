<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class EformsCodelistSeeder extends Seeder
{
    public function run(): void
    {
        $data = json_decode(
            file_get_contents(database_path('data/eforms_codelists.json')),
            true,
            512,
            JSON_THROW_ON_ERROR
        );

        DB::transaction(function () use ($data) {
            foreach ($data['lists'] as $table => $list) {
                if (empty($list['rows'])) {
                    continue;
                }

                DB::table($table)->upsert($list['rows'], ['code'], ['label_sk']);
            }
        });
    }
}