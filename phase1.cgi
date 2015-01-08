#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use HTML::FillInForm;
use SFCON::Register;

#定数定義
require('pgreglib.pl');
our %CONDEF_CONST;
my $c_not_fill = 'bgcolor="red"';

my $register = SFCON::Register->new;
my $cgi=CGI->new;

# セッションID = urlパラメータ||cookieからCGISESSID||取得できなかったらundef．
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
#セッションIDに基づきセッション取得 セッションIDが無効なら新たに発行
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

# 画面表示前処理
my $input_page  = undef; # HTML表示テンプレート
my $fobject     = undef; # HTML FormFillパラメータ
my $html_out    = undef; # 出力するHTML
my @Ahttp_head  = ( -charset => 'UTF-8', );

if ( defined $sid && $sid eq $session->id ) { # 取得したセッションidが有効
    # 申し込み画面 or 確認画面表示準備
    $input_page = HTML::Template->new(filename => 'phase1-tmpl.html');
	if($session->param('phase') ne '1-2' || $cgi->param('self') ne 'true') {
        # 申し込み画面初期表示準備
		$session->param('phase','1-2');
        $fobject    = $session;
	} else {
        # 申し込み受付時チェック
		if ( _input_check($cgi, $input_page) ) {
            # 入力内容不備時 申込画面再表示準備
			$fobject    = $cgi;
		} else {
            # チェック成功 -> 入力値をセッションに保存し、phase2にredirect
			$session->save_param($cgi);
            my $urlparam =
                ($cgi->cookie('ID') eq  $session->id) ? '' : '?ID=' . $sid;
            $input_page = undef;
			$html_out = $cgi->redirect('./phase2.cgi' . $urlparam);
		}
	}
} else {    # セッションタイムアウト
    # まずセッション開放
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
    # エラー画面表示準備
    $input_page = HTML::Template->new(filename => 'error.html');
	my $cookie_path = $ENV{SCRIPT_NAME};
	$cookie_path =~ s/[^\/]+$//g ;
	my $cookie = $cgi->cookie(  -name => "ID",     -value => "$sid",
                                -expires => "+3h", -path => "$cookie_path");
    push( @Ahttp_head, ( -expires => 'now', -cookie => $cookie));
}

if ( $input_page ) { # リダイレクトではない
    # HTMLテンプレート変数置き換え
	$input_page->param(ID => $sid);
    $input_page->param(CONNAME   => $CONDEF_CONST{'CONNAME'});
    $input_page->param(FULLNAME  => $CONDEF_CONST{'FULLNAME'});
    $input_page->param(CONPERIOD => $CONDEF_CONST{'CONPERIOD'});
    # CGIパラメータ置き換え
    if ( $fobject ) {
        my $form_out = HTML::FillInForm->new;
		$html_out = $form_out->fill(
			                        scalarref => \$input_page->output,
			                        target => "mailform",
			                        fobject => $fobject,
		                        );
    } else {
        $html_out = $input_page->output;
    }
    # リダイレクトでない場合のみ、HTTPヘッダを出力
	print $cgi->header(@Ahttp_head);
	print "\n\n";
}

# HTML本体出力
print $html_out;
exit;

# 入力値チェック
sub _input_check {
	my (
        $cgi,       # CGIオブジェクト
        $page,      # HTML::Templateオブジェクト
    ) = @_;

    ## チェックテーブル定義
    # 必須項目テーブル
    #   入力項目名 => TMPL変数名
    my %needs_tbl = (
        # 主催者情報
        'p1_name'   => 'C_P1_NAME',         # 名前
	    'email'     => 'C_CO_EMAIL',        # メールアドレス
	    'reg_num'   => 'C_CO_REG_NUMBER',   # 参加登録番号
                                        # 電話番号、FAX番号、携帯番号は省略可能
        # 企画情報
	    'pg_name'   => 'C_CO_PG_NAME',      # 企画名称
	    'pg_name_f' => 'C_CO_PG_NAME_F',    # 企画名称フリガナ
	    'pg_kind'   => 'C_CO_PG_KIND',      # 企画種別
	    'pg_place'  => 'C_CO_PG_PLACE',     # 希望場所
	    'pg_layout' => 'C_CO_PG_PLACE',     # 希望場所レイアウト
	    'pg_time'   => 'C_CO_PG_TIME',      # 希望日時
	    'pg_koma'   => 'C_CO_PG_KOMA',      # 希望コマ数
	    'pg_ninzu'  => 'C_CO_PG_NINZU',     # 予想参加者
	    'pg_naiyou' => 'C_CO_PG_NAIYOU',    # 内容説明
        'pg_naiyou_k'   => 'C_CO_PG_NAIYOU',    # 内容説明
	    'pg_kiroku_kb'  => 'C_CO_PG_KIROKU_KB', # リアルタイム公開
	    'pg_kiroku_ka'  => 'C_CO_PG_KIROKU_KA', # 事後公開
	    'pg_enquete'    => 'C_CO_PG_ENQUETE',   # 企画を立てるのは
        'youdo'     => 'C_CO_PG_YOUDO',     # 申込者の出演
    );
    # 本数チェックテーブル (0より大)
    # 条件変数名 => [ チェック変数名, TMPL変数名 ]
    my %count_tbl = (
        'mic'       => [ 'miccnt',  'C_CO_PG_KIZAI', ],
        'mic2'      => [ 'mic2cnt', 'C_CO_PG_KIZAI', ],
    );
    # fc_vid必須項目テーブル
    my %fc_vid_needs_tbl = (
        'av-v'  => 'C_CO_PG_KIZAI',
        'av-a'  => 'C_CO_PG_KIZAI',
    );
    # fc_pc必須項目テーブル
    my %fc_pc_needs_tbl = (
        'pc-v'  => 'C_CO_PG_KIZAI',
        'pc-a'  => 'C_CO_PG_KIZAI',
        'lan'   => 'C_CO_PG_KIZAI',
    );
    # 条件付き必須チェックテーブル
    #   条件変数名 => [ 条件値, チェック変数名, TMPL変数名 ]
    my %cond_tbl = (
        'pg_kind'   =>  [ 'K-X1',  'pg_kind2',   'C_CO_PG_KIND', ],
	    'pg_place'  =>  [ 'P-X1',  'pg_place2',  'C_CO_PG_PLACE', ],
	    'pg_layout' =>  [ '9',     'pg_layout2', 'C_CO_PG_PLACE', ],
	    'pg_time'   =>  [ 'T-X1',  'pg_time2',   'C_CO_PG_TIME', ],
	    'pg_koma'   =>  [ 'TK-X1', 'pg_koma2',   'C_CO_PG_KOMA', ],
    );
    # 条件付き値固定チェックテーブル
    #   条件変数名 => [ 条件値, チェック変数名, 固定値, TMPL変数名 ]
    my %cond_fix_tbl = (
	    'pg_place'  =>  [ 'P-H1',  'pg_layout',  '0', 'C_CO_PG_PLACE', ],
    );
    # fc_vid条件付き必須チェックテーブル
    my %fc_vid_cond_tbl = (
        'av-v'  =>  [ 'other', 'av-v_velse',  'C_CO_PG_KIZAI', ],
        'av-a'  =>  [ 'other', 'av-a_velse',  'C_CO_PG_KIZAI', ],
    );
    # fc_pc条件付きチェックテーブル
    my %fc_pc_cond_tbl = (
        'pc-v'  =>  [ 'other', 'pc-v_velse',  'C_CO_PG_KIZAI', ],
        'pc-a'  =>  [ 'other', 'pc-a_velse',  'C_CO_PG_KIZAI', ],
        'lan'   =>  [ 'other', 'pc-l_velse',  'C_CO_PG_KIZAI', ],
    );

    my %AfailVnames = ();   # エラーTMPL変数名ハッシュ(値はダミー)
	
    # 必須項目チェック
    while ( my ( $pname, $vname ) = each( %needs_tbl ) ) {
        if ( $cgi->param($pname) eq '' ) {
            $AfailVnames{$vname} = 1;
        }
    }
    # 条件付き必須チェック
    while ( my ( $pname, $vAprm ) = each( %cond_tbl ) ) {
        if (    ( $cgi->param($pname) eq $vAprm->[0] )
             && ( $cgi->param($vAprm->[1]) eq '' ) ) {
            $AfailVnames{$vAprm->[2]} = 1;
        }
    }
    # 条件付き値固定チェック
    while ( my ( $pname, $vAprm ) = each( %cond_fix_tbl ) ) {
#        die "pname:$pname\nvAprm:$vAprm->[0]:$vAprm->[1]:$vAprm->[2]\n"
#            . 'cgi->ppval:' . $cgi->param($pname) . "\n"
#            . 'cgi->cpval:' . $cgi->param($vAprm->[1]) . "\n";
        if (    ( $cgi->param($pname) eq $vAprm->[0] )
             && ( $cgi->param($vAprm->[1]) ne $vAprm->[2] ) ) {
            $AfailVnames{$vAprm->[3]} = 1;
        }
    }

    # 使用機材
    while ( my ( $pname, $vAprm ) = each( %count_tbl ) ) {
        if (    ( $cgi->param($pname) )
             && ( $cgi->param($vAprm->[0]) <= 0 ) ) {
            $AfailVnames{$vAprm->[1]} = 1;
        }
	}

    if ( $cgi->param('fc_vid') eq '0' ) {
        # 必須項目チェック
        while ( my ( $pname, $vname ) = each( %fc_vid_needs_tbl ) ) {
            if ( $cgi->param($pname) eq '' ) {
                $AfailVnames{$vname} = 1;
            }
        }
        # 条件付き必須チェック
        while ( my ( $pname, $vAprm ) = each( %fc_vid_cond_tbl ) ) {
            if (    ( $cgi->param($pname) eq $vAprm->[0] )
                 && ( $cgi->param($vAprm->[1]) eq '' ) ) {
                $AfailVnames{$vAprm->[2]} = 1;
            }
        }
    }
    if ( $cgi->param('fc_pc') eq '0' ) {
        # 必須項目チェック
        while ( my ( $pname, $vname ) = each( %fc_pc_needs_tbl ) ) {
            if ( $cgi->param($pname) eq '' ) {
                $AfailVnames{$vname} = 1;
            }
        }
        # 条件付き必須チェック
        while ( my ( $pname, $vAprm ) = each( %fc_pc_cond_tbl ) ) {
            if (    ( $cgi->param($pname) eq $vAprm->[0] )
                 && ( $cgi->param($vAprm->[1]) eq '' ) ) {
                $AfailVnames{$vAprm->[2]} = 1;
            }
        }
        # 回線理由
        if ( ( $cgi->param('lan') ne 'none' )  &&
             ( $cgi->param('lanreason') eq '' )   ) {
            $AfailVnames{'C_CO_PG_KIZAI'} = 1;
        }
	}

    # 出演者情報
    my $ppcnt;
	for ($ppcnt = 1; $ppcnt <= 8; $ppcnt++) {	# CONST: 出演者の最大値
        my $ppname      = 'pp' . $ppcnt . '_name';
        my $ppname_f    = 'pp' . $ppcnt . '_name_f';
        my $ppcon       = 'pp' . $ppcnt . '_con';
        my $ppgrq       = 'pp' . $ppcnt . '_grq';
        my $CCOPG       = 'C_CO_PG_GUEST' . $ppcnt;
	    if ($cgi->param($ppname) ne '' || $cgi->param($ppname_f) ne ''){
		    if ($cgi->param($ppname) eq '' || $cgi->param($ppname_f) eq '' ||
                $cgi->param($ppcon)  eq '' || $cgi->param($ppgrq) eq ''){
                $AfailVnames{$CCOPG} = 1;
		    }
	    }
    }
    foreach my $vname ( keys( %AfailVnames ) ) {
        $page->param($vname => $c_not_fill);
    }

	return( scalar(%AfailVnames) ? 1 : 0 );
}

sub _is_blank {
    return ( $_[0] eq '' );
}
sub _ne_blank {
    return ( $_[0] ne '' );
}

1;
#end
